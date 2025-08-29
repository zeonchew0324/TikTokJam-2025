import requests

def handle_flagged_content(video_id, similarity_score):
    api_endpoint = "https://your-api-endpoint.com/api/video/receive-creator-bots"
    
    params = {
        "videoId": video_id,
        "similarityScore": similarity_score
    }
    
    response = requests.post(api_endpoint, params=params)
    
    if response.status_code == 200:
        print(f"Successfully flagged video {video_id} as potential bot content.")
    else:
        print(f"Failed to flag video {video_id}. "
              f"Status code: {response.status_code}, Response: {response.text}")
