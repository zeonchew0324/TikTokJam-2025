import os
import uuid
from ai.tech_stack.aws import upload_to_s3
from ai.tech_stack.twelve_labs import create_video_embedding
from ai.tech_stack.qdrant import store_video_in_qdrant
from ai.bot_content_detection.main import detect_similar_videos
from ai.bot_content_detection.handle_flagged_content import handle_flagged_content

# Get a list of video files
video_dir = "ai/video_content"
video_files = [f for f in os.listdir(video_dir) if f.endswith('.mp4')]

# Function to embed a single video file
def embed_single_video(filename):
    print(f"\nProcessing {filename}...")
    video_path = os.path.join(video_dir, filename)
    video_id = f"{str(uuid.uuid4())[:8]}_{filename}"
    
    # Upload video to S3
    s3_url = upload_to_s3(video_path, video_id)
    
    # Generate video embeddings using Twelve Labs
    video_embedding = create_video_embedding(s3_url)
    
    # Run the bot content detection
    similar_videos = detect_similar_videos(video_embedding)
    
    if not similar_videos:
        # Store video embeddings in Qdrant
        store_video_in_qdrant(video_embedding, video_id, s3_url, filename)
        
        print(f"Successfully processed {filename}")
    else:
        # Handle flagged content (i.e., notify via API)
        similarity_score = round(float(similar_videos[0][2]) * 100, 2)
        print(f"Similarity score: {similarity_score}, Type: {type(similarity_score)}")
        handle_flagged_content(video_id, filename)
        
        print(f"Video {filename} flagged as potential bot-generated content due to similarity with existing videos.")
        
# Function to reembed single video file
def reembed_single_video(video_id, s3_url):# Generate video embeddings using Twelve Labs
    video_embedding = create_video_embedding(s3_url)
    
    # Store video embeddings in Qdrant
    store_video_in_qdrant(video_embedding, video_id, s3_url)
    
    print(f"Successfully re-embedded {video_id}")

# Function to embed videos from the video_content directory
def embed_videos():
    for filename in video_files:
        try:
            print(f"\nProcessing {filename}...")
            video_path = os.path.join(video_dir, filename)
            video_id = f"{str(uuid.uuid4())[:8]}_{filename}"
            
            # Upload video to S3
            s3_url = upload_to_s3(video_path, video_id)
            
            # Generate video embeddings using Twelve Labs
            video_embedding = create_video_embedding(s3_url)
            
            # Run the bot content detection
            similar_videos = detect_similar_videos(video_embedding)
            
            if not similar_videos:
                # Store video embeddings in Qdrant
                store_video_in_qdrant(video_embedding, video_id, s3_url)
                
                print(f"Successfully processed {filename}")
            else:
                # Handle flagged content (i.e., notify via API)
                similarity_score = round(float(similar_videos[0][2]) * 100, 2)
                print(f"Similarity score: {similarity_score}, Type: {type(similarity_score)}")
                handle_flagged_content(video_id, similarity_score)
        
                print(f"Video {filename} flagged as potential bot-generated content due to similarity with existing videos.")
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            
if __name__ == "__main__":
    embed_videos()