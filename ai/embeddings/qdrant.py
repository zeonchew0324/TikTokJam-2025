import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from prepare_embedding import prepare_embedding
from dotenv import load_dotenv

load_dotenv()

# Qdrant Configuration
COLLECTION_NAME = "video_embeddings"
VECTOR_SIZE = 2048

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_ENDPOINT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=20,
    prefer_grpc=False
)

# Create qdrant collection if not exists
if not qdrant_client.collection_exists(COLLECTION_NAME):
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )
    print(f"✅ Created collection: {COLLECTION_NAME}")
else:
    print(f"⚡ Collection already exists: {COLLECTION_NAME}")

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
                raise ValueError("No clip-scope embedding found")
        else:
            raise ValueError("No embeddings found in the response")

        # Prepare embedding from video segments
        embedding_vector = prepare_embedding(video_segments)

        # Create a unique point structure for Qdrant storage
        point = PointStruct(
            id=uuid.uuid4().int & ((1<<64)-1), # Generate a unique 64-bit integer ID
            vector=embedding_vector, # Store the extracted embedding vector
            payload={
                'video_id': video_id,
                'video_url': s3_url,  # Store the public S3 URL of the video
                'is_url': True,
                'original_filename': original_filename # Save the original filename
            }
        )

        # Insert points
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=[point])
        print(f"Stored whole video embedding in Qdrant")
    except Exception as e:
        print(f"Error storing in Qdrant: {str(e)}")
        raise