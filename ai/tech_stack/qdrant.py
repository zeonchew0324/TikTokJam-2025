import os
import uuid
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
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
def store_in_qdrant(video_embedding, video_id, s3_url):
    if not qdrant_client:
        raise ValueError("Qdrant client not configured")

    try:
        print(f"Storing video embedding for {video_id}...")

        # Create a unique point structure for Qdrant storage
        point = PointStruct(
            id=uuid.uuid4().int & ((1<<64)-1), # Generate a unique 64-bit integer ID
            vector=video_embedding, # Store the extracted embedding vector
            payload={
                'video_id': video_id,
                'video_url': s3_url,  # Store the public S3 URL of the video
            }
        )

        # Insert points
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=[point])
        print(f"Stored whole video embedding in Qdrant")
    except Exception as e:
        print(f"Error storing in Qdrant: {str(e)}")
        raise

# Function to retrieve single video embedding from qdrant using video id
def retrieve_single_from_qdrant(point_id):
    if not qdrant_client:
        raise ValueError("Qdrant client not configured")

    try:
        print(f"Retrieving video embedding for {point_id}...")

        retrieved_points = qdrant_client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[point_id],
            with_vectors=True,
            with_payload=True
        )

        if retrieved_points:
            point = retrieved_points[0]
            vector_embedding = point.vector
            payload = point.payload

            print(f"Retrieved Vector: {vector_embedding}")
            print(f"Retrieved Payload: {payload}")
            return np.array(vector_embedding, dtype=np.float32)
        else:
            print(f"Point with ID {point_id} not found in collection {COLLECTION_NAME}.")
    except Exception as e:
        print(f"Error retrieving from Qdrant: {str(e)}")
        raise
    
# Function to retrieve all video embeddings from qdrant
def retrieve_all_from_qdrant():
    if not qdrant_client:
        raise ValueError("Qdrant client not configured")

    try:
        print(f"Retrieving all video embeddings...")

        all_vectors = []

        # Iterate through all points in the collection
        # The scroll method returns points and a next_page_offset for pagination
        next_page_offset = None
        while True:
            points, next_page_offset = qdrant_client.scroll(
                collection_name=COLLECTION_NAME,
                limit=100,  # Adjust limit as needed for performance
                offset=next_page_offset,
                with_vectors=True,
                with_payload=True # Include payload if desired
            )
            if not points:
                break # No more points to retrieve

            for point in points:
                vector_embedding = np.array(point.vector, dtype=np.float32)
                all_vectors.append(vector_embedding) # Access the vector embedding

            if next_page_offset is None:
                break # Reached the end of the collection

        print(f"Retrieved {len(all_vectors)} vector embeddings.")
        return np.array(all_vectors, dtype=np.float32)
    except Exception as e:
        print(f"Error retrieving all from Qdrant: {str(e)}")
        raise
    
# Function to retrieve video url from qdrant using video embedding
def retrieve_video_url_by_embedding(query_vector, limit=1, score_threshold=0.9):
    if not qdrant_client:
        raise ValueError("Qdrant client not configured")
    
    try:
        search_result = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold
        )
        
        if search_result and len(search_result) > 0:
            # Get the most similar result
            best_match = search_result[0]
            
            # Extract video_url from payload
            if hasattr(best_match, 'payload') and 'video_url' in best_match.payload:
                return best_match.payload['video_url']
        
        return None
        
    except Exception as e:
        print(f"Error retrieving video URL: {e}")
        raise