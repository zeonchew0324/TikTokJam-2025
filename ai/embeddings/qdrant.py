import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

load_dotenv()

# Qdrant Configuration
QDRANT_HOST = "YOUR_QDRANT_HOST"
COLLECTION_NAME = "content_collection"
VECTOR_SIZE = 1024  # Size of embeddings from Twelve Labs

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=f"https://{os.getenv('QDRANT_HOST')}",
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=20,
    prefer_grpc=False
)

# Function to store embed video in qdrant
def store_in_qdrant(task_result, video_id, s3_url, original_filename):
    if not qdrant_client:
        raise ValueError("Qdrant client not configured")

    try:
        print(f"Processing video embedding for {video_id}...")

        # The embedding will be in the segments with embedding_scope="clip"
        if task_result.video_embedding and task_result.video_embedding.segments:
            video_segments = [s for s in task_result.video_embedding.segments
                             if hasattr(s, 'embedding_scope') and s.embedding_scope == 'clip']

            if video_segments:
                print(f"Found clip-scope embedding")
        else:
            raise ValueError("No embeddings found in the response")

        def create_collection_if_not_exists(name: str, size: int = 1024):
            if not qdrant_client.collection_exists(name):
                qdrant_client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=size, distance=Distance.COSINE)
                )
                print(f"✅ Created collection: {name}")
            else:
                print(f"⚡ Collection already exists: {name}")

        # Create collections
        create_collection_if_not_exists("video_visual_embeddings")
        create_collection_if_not_exists("video_audio_embeddings")

        # Example point structure
        visual_points = []
        audio_points = []

        for segment in video_segments:
            # Visual embedding point
            segment_id = segment.start_offset_sec / 6 + 1
            if segment.embedding_option == "visual-text":
                visual_point = PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{video_id}_visual_{segment_id}")),
                    vector=segment.float_,
                    payload={
                        "video_id": video_id,
                        "start_time": segment.start_offset_sec,
                        "end_time": segment.end_offset_sec,
                        "segment_id": segment_id,
                        "duration": segment.end_offset_sec - segment.start_offset_sec,
                        "embedding_type": "visual-text",
                        "source": "twelvelabs_clip"
                    }
                )

                visual_points.append(visual_point)

            elif segment.embedding_option == "audio":
                audio_point = PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{video_id}_audio_{segment_id}")),
                    vector=segment.float_,
                    payload={
                        "video_id": video_id, 
                        "start_time": segment.start_offset_sec,
                        "end_time": segment.end_offset_sec,
                        "segment_id": segment_id,
                        "duration": segment.end_offset_sec - segment.start_offset_sec,
                        "embedding_type": "audio",
                        "source": "twelvelabs_clip"
                    }
                )

                audio_points.append(audio_point)

            else:
                print(f"No visual-text or audio embeddings found in the clip segment")

        # Insert points
        qdrant_client.upsert(collection_name="video_visual_embeddings", points=visual_points)
        qdrant_client.upsert(collection_name="video_audio_embeddings", points=audio_points)
        print(f"Stored whole video embeddings in Qdrant")
    except Exception as e:
        print(f"Error storing in Qdrant: {str(e)}")
        raise