from ai.cluster_videos.main import cluster_videos_into_category
from ai.tech_stack.qdrant import retrieve_all_from_qdrant, VIDEO_COLLECTION_NAME, CENTROID_COLLECTION_NAME
from ai.visualize_clustering_algo.visualize_clusters import project_embeddings_to_3d

def visualize_clustering_algo():
    cluster_videos_into_category()
    
    video_embeddings = retrieve_all_from_qdrant(VIDEO_COLLECTION_NAME)
    centroid_embeddings = retrieve_all_from_qdrant(CENTROID_COLLECTION_NAME)

    if video_embeddings is None: 
        print("No video embeddings found.")
        return
    
    if centroid_embeddings is None or len(centroid_embeddings) == 0:
        print("No centroid embeddings found.")
        return
    
    print("Visualizing video and centroid embeddings...")
    return project_embeddings_to_3d(video_embeddings, centroid_embeddings)