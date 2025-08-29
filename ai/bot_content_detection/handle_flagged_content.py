import requests

def handle_flagged_content(video_id):
    endpoint_url = "https://your-api-endpoint.com/flagged-videos"  # Replace with your actual endpoint
    
    payload = {
        "video_id": video_id
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(endpoint_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print(f"Successfully flagged video {video_id} as potential bot content.")
    else:
        print(f"Failed to flag video {video_id}. Status code: {response.status_code}, Response: {response.text}")