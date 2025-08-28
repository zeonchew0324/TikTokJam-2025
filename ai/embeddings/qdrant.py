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

        # Create collections
        qdrant_client.create_collection(
            collection_name="video_visual_embeddings",
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )

        qdrant_client.create_collection(
            collection_name="video_audio_embeddings", 
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )

        # Example point structure
        visual_points = []
        audio_points = []

        for segment in video_segments:
            # Visual embedding point
            if segment.embedding_option == "visual-text":
                visual_point = PointStruct(
                    id=f"{video_id}_visual_{segment.start_offset_sec / 6 + 1}",
                    vector=segment.float_,
                    payload={
                        "video_id": video_id,
                        "start_time": segment.start_offset_sec,
                        "end_time": segment.end_offset_sec,
                        "segment_index": segment.id,
                        "duration": segment.end_offset_sec - segment.start_offset_sec,
                        "embedding_type": "visual-text",
                        "source": "twelvelabs_clip"
                    }
                )

                visual_points.append(visual_point)

            elif segment.embedding_option == "audio":
                audio_point = PointStruct(
                    id=f"{video_id}_audio_{segment.start_offset_sec / 6 + 1}",
                    vector=segment.float_,
                    payload={
                        "video_id": video_id, 
                        "start_time": segment.start_offset_sec,
                        "end_time": segment.end_offset_sec,
                        "segment_index": segment.id,
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