import os
import uuid
import boto3
import subprocess
from botocore.exceptions import ClientError
import requests
from IPython.display import display, HTML
import shutil
import pandas as pd
from twelvelabs import TwelveLabs
from qdrant_client import QdrantClient, models
from qdrant_client.models import PointStruct
import time
from dotenv import load_dotenv

load_dotenv()

AWS_BUCKET_NAME = "tiktok-video-embeddings"
AWS_REGION = "ap-southeast-1"  # Change to your region

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    region_name=AWS_REGION
)

# Twelve Labs Configuration
twelvelabs_client = TwelveLabs(api_key=os.getenv("TL_API_KEY"))

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

# Get a list of video files
video_dir = "ai/video_content"
video_files = [f for f in os.listdir(video_dir) if f.endswith('.mp4')]

# Function to validate video file 
def validate_video_file(file_path):
    """Validate video file using ffprobe"""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', '-show_streams', file_path
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"ffprobe failed for {file_path}")
            return False
            
        import json
        probe_data = json.loads(result.stdout)
        
        # Check if file has video streams
        video_streams = [s for s in probe_data.get('streams', []) if s.get('codec_type') == 'video']
        if not video_streams:
            print(f"No video streams found in {file_path}")
            return False
            
        # Check duration
        duration = float(probe_data.get('format', {}).get('duration', 0))
        if duration < 0.1:  # Less than 0.1 seconds
            print(f"Video too short: {duration}s")
            return False
            
        print(f"Video validation passed - Duration: {duration}s, Streams: {len(video_streams)}")
        return True
        
    except Exception as e:
        print(f"Error validating video {file_path}: {str(e)}")
        return False

#Function to upload videos to S3
def upload_to_s3(file_path, filename):
    try:
        if not validate_video_file(file_path):
            raise ValueError("Invalid video file")
        # Upload the file
        s3_client.upload_file(
            file_path,
            AWS_BUCKET_NAME,
            f"videos-embed/{filename}",
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': 'video/mp4'
            }
        )

        # Generate the public URL
        url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/videos-embed/{filename}"
        print(f"Uploaded to S3: {url}")
        return url

    except ClientError as e:
        print(f"Error uploading to S3: {str(e)}")
        raise

# Function to fetch video embeddings 
def create_video_embedding(video_path, max_retries=3, retry_delay=5):
    if not twelvelabs_client:
        raise ValueError("Twelve Labs API key not configured")

    retries = 0
    while retries < max_retries:
        try:
            print(f"Creating whole video embedding for {video_path}... (Attempt {retries+1}/{max_retries})")

            # Use video_embedding_scopes parameter set to ["clip", "video"] to get whole video embedding
            task = twelvelabs_client.embed.tasks.create(
                model_name="Marengo-retrieval-2.7",
                video_file=video_path,
                video_embedding_scope=["clip", "video"]
            )

            print(f"Created task: id={task.id}, status={task.status}")
            task.wait_for_done(sleep_interval=3)
            task_result = twelvelabs_client.embed.tasks.retrieve(task.id)

            if task_result.status != 'ready':
                raise ValueError(f"Task failed with status: {task_result.status}")

            return task_result

        except Exception as e:
            print(f"Error creating embedding (attempt {retries+1}): {str(e)}")
            retries += 1
            if retries < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print("Max retries reached, giving up.")
                raise
            
            # Function to store embed video in qdrant
def store_in_qdrant(task_result, video_id, s3_url, original_filename):
    if not qdrant_client:
        raise ValueError("Qdrant client not configured")

    try:
        print(f"Processing video embedding for {video_id}...")

        # The embedding will be in the segments with embedding_scope="video"
        if task_result.video_embedding and task_result.video_embedding.segments:
            video_segments = [s for s in task_result.video_embedding.segments
                             if hasattr(s, 'embedding_scope') and s.embedding_scope == 'video']

            if video_segments:
                print(f"Found video-scope embedding")
                embedding_vector = video_segments[0].embeddings_float
            else:
                # If no video scope segment is found, use the first segment as fallback
                print(f"No video-scope embedding found, using first available segment")
                embedding_vector = task_result.video_embedding.segments[0].embeddings_float
        else:
            raise ValueError("No embeddings found in the response")

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

	 # Insert the generated embedding point into the Qdrant collection
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=[point])
        print(f"Stored whole video embedding in Qdrant")
        return 1
    except Exception as e:
        print(f"Error storing in Qdrant: {str(e)}")
        raise


# Embedding Pipeline
for filename in video_files[:5]:  # Process first 5 videos or you can setup as per convenience
    try:
        print(f"\nProcessing {filename}...")
        video_path = os.path.join(video_dir, filename)
        video_id = f"{str(uuid.uuid4())[:8]}_{filename}"
        
        # Upload to S3
        s3_url = upload_to_s3(video_path, video_id)
        print(f"S3 url: {s3_url}")
        
        # Generate embeddings
        task_result = create_video_embedding(video_path)
        
        # Store in Qdrant
        store_in_qdrant(task_result, video_id, s3_url, filename)
        
        print(f"Successfully processed {filename}")
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")