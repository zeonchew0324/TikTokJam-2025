from ai.tech_stack.qdrant import retrieve_video_url_by_embedding, store_category_in_qdrant
from ai.tech_stack.twelve_labs import categorize_video

def label_centroids(centroid_categories):
    for centroid_embedding, nearest_video_embedding in centroid_categories:
        video_url = retrieve_video_url_by_embedding(nearest_video_embedding)
        category = categorize_video(video_url)
        store_category_in_qdrant(centroid_embedding, category)
        print(f"Labeled centroid with category: {category}")