import os
import uuid
from aws import upload_to_s3
from twelve_labs import create_video_embedding
from qdrant import store_in_qdrant

# Get a list of video files
video_dir = "ai/video_content"
video_files = [f for f in os.listdir(video_dir) if f.endswith('.mp4')]

# Embedding Pipeline
for filename in video_files[:5]:  # Process first 5 videos or you can setup as per convenience
    try:
        print(f"\nProcessing {filename}...")
        video_path = os.path.join(video_dir, filename)
        video_id = f"{str(uuid.uuid4())[:8]}_{filename}"
        
        # Upload video to S3
        s3_url = upload_to_s3(video_path, video_id)
        
        # Generate video embeddings using Twelve Labs
        task_result = create_video_embedding(s3_url)
        
        # Store video embeddings in Qdrant
        store_in_qdrant(task_result, video_id, s3_url, filename)
        
        print(f"Successfully processed {filename}")
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")