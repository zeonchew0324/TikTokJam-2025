from concurrent.futures import ThreadPoolExecutor, as_completed
from ai.tech_stack.aws import retrieve_single_s3_url_by_video_id
from ai.tech_stack.gemini import score_video_normalized

def evaluate_video_quality(video_id):
    s3_url = retrieve_single_s3_url_by_video_id(video_id)
    
    if not s3_url:
        print(f"No S3 URL found for video ID: {video_id}")
        return -1.0
    
    quality_score = score_video_normalized(s3_url)
    return quality_score

def evaluate_video_quality_batch(video_id_list, max_workers=8):
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(evaluate_video_quality, vid): vid for vid in video_id_list}
        
        for future in as_completed(future_to_id):
            vid = future_to_id[future]
            try:
                results[vid] = future.result()
            except Exception as e:
                print(f"Error processing video {vid}: {e}")
                results[vid] = -1.0
    
    return results
