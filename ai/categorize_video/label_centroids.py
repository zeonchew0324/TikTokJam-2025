from ai.tech_stack.qdrant import retrieve_video_url_by_embedding
from ai.tech_stack.twelve_labs import categorize_video

def label_centroids(centroid_categories):
    labeled_centroids = []
    for centroid_embedding, nearest_video_embedding in centroid_categories:
        video_url = retrieve_video_url_by_embedding(nearest_video_embedding)
        category = categorize_video(video_url)
        labeled_centroids.append({category: centroid_embedding})
        
    return labeled_centroids