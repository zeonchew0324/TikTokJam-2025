from ai.tech_stack.qdrant import retrieve_all_from_qdrant, VIDEO_COLLECTION_NAME
from ai.tech_stack.faiss_algo import cluster_videos
from ai.cluster_videos.label_centroids import label_centroids

def cluster_videos_into_category():
    # Retrieve all video embeddings from Qdrant
    video_embeddings = retrieve_all_from_qdrant(collection_name=VIDEO_COLLECTION_NAME)
    
    if video_embeddings.size is None:
        print("No video embeddings found in Qdrant.")
        return
    
    # Cluster video embeddings using FAISS KMeans
    centroid_categories = cluster_videos(video_embeddings)
    
    # Label centroids with categories and store in Qdrant
    label_centroids(centroid_categories)
    
    # Visualize the clustering result
    
    print("Clustered videos of the same category into one cluster.")