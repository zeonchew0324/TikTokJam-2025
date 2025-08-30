import requests

def post_video_into_java_server(video_id, s3_url, quality_score):
    api_endpoint = "https://your-api-endpoint.com/api/video/upload"
    
    params = {
        "videoId": video_id,
        "s3Url": s3_url,
        "qualityScore": quality_score,
    }
    
    response = requests.post(api_endpoint, params=params)
    
    if response.status_code == 200:
        print(f"Successfully upload video into java server.")
    else:
        print(f"Failed to upload video {video_id}. "
              f"Status code: {response.status_code}, Response: {response.text}")