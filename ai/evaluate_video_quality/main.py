from ai.tech_stack.aws import retrieve_single_s3_url_by_video_id
from ai.tech_stack.gemini import score_video_normalized

def evaluate_video_quality(video_id):
    s3_url = retrieve_single_s3_url_by_video_id(video_id)
    
    if not s3_url:
        print(f"No S3 URL found for video ID: {video_id}")
        return -1.0
    
    quality_score = score_video_normalized(s3_url)
    
    return quality_score