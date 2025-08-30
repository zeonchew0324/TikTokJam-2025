from ai.tech_stack.qdrant import retrieve_all_from_qdrant, VIDEO_COLLECTION_NAME, CENTROID_COLLECTION_NAME
from ai.visualize_clustering_algo.visualize_clusters import project_embeddings_to_3d

def visualize_clustering_algo():
    video_embeddings = retrieve_all_from_qdrant(VIDEO_COLLECTION_NAME)
    centroid_embeddings = retrieve_all_from_qdrant(CENTROID_COLLECTION_NAME)

    if video_embeddings is None: 
        print("No video embeddings found.")
        return
    
    if centroid_embeddings is None or len(centroid_embeddings) == 0:
        print("No centroid embeddings found.")
        return
    
    print("Visualizing video and centroid embeddings...")
    video_embeddings_3d, centroid_embeddings_3d = project_embeddings_to_3d(video_embeddings, centroid_embeddings)
    
    video_embeddings_3d = video_embeddings_3d.tolist()
    centroid_embeddings_3d = centroid_embeddings_3d.tolist()
    
    return video_embeddings_3d, centroid_embeddings_3d

"""
# Code for 3D scatter plot visualization
import numpy as np
vidproj, centproj = visualize_clustering_algo()
vidproj = np.array(vidproj)
centproj = np.array(centproj)

import matplotlib.pyplot as plt
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')  # Create 3D axes

ax.scatter(vidproj[:, 0], vidproj[:, 1], vidproj[:, 2], c='b', marker='o', label='Video Embeddings', alpha=0.5)
ax.scatter(centproj[:, 0], centproj[:, 1], centproj[:, 2], c='r', marker='^', s=100, label='Centroids')

ax.set_xlabel('PCA 1')
ax.set_ylabel('PCA 2')
ax.set_zlabel('PCA 3')

plt.title('3D PCA Projection of Video Embeddings and Centroids')
ax.legend()
plt.show()
"""