print("running Faiss Clustering")

'''
This module is responsible for clustering video embeddings using FAISS.
It will receive vidembed as video embeddings in the form of a 2D numpy array.
vidembed will be nb*2048 dimension where nb is the number of video embeddings
Then it will return an array of centroids. 


'''




import faiss                   # make faiss available, and gpu can be enabled later
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from sklearn.decomposition import PCA
from ai.tech_stack.qdrant import retrieve_single_from_qdrant, retrieve_all_from_qdrant

ncentroids = 4 # the number of centroids

niter = 20
verbose = True

def cluster_videos(vidembed, ncentroids=100, niter=20, verbose=True):
    """
    Clusters video embeddings using FAISS KMeans and assigns each centroid to its nearest video embedding.

    Args:
        vidembed (np.ndarray): 2D numpy array of shape (nb, 2048) containing video embeddings.
        ncentroids (int): Number of centroids/clusters to form.
        niter (int): Number of iterations for KMeans training.
        verbose (bool): If True, prints FAISS KMeans training progress.

    Returns:
        List[Tuple[np.ndarray, np.ndarray]]: List of tuples, each containing a centroid embedding and its nearest video embedding.
    """

    #since we are going to use l2distance for similarity, the input needs to be l2 normalized
    vidembed = vidembed / np.linalg.norm(vidembed, axis=1, keepdims=True)

    d = vidembed.shape[1]
    kmeans = faiss.Kmeans(d, ncentroids, niter=niter, verbose=verbose)
    kmeans.train(vidembed)

    centroids = kmeans.centroids

    vidind = faiss.IndexFlatL2(d)
    vidind.add(vidembed)

    centroid_categories = []
    for centroid in centroids:
        D, I = vidind.search(centroid.reshape(1, -1), k=1)
        centroid_categories.append((centroid, vidembed[I[0][0]]))

    return centroid_categories


def categorize_video(vidquery, centroids, k=3):
    '''
    for each video in vidquery, find k most similar centroids to it, where the precalculated centroid is given by centroids
    Args:
        vidquery (np.ndarray): 2D numpy array of shape (nb, 2048) containing video query embeddings.
        centroids (np.ndarray): 2D numpy array of shape (ncentroids, 2048) containing centroid embeddings.
    Returns: List[Tuple((centroid_embedding1,cosine similarity1), (centroid_embedding2, cosine similarity2), (centroid_embedding3, cosine similarity3))]
    eg for 1 video [((centroid_embedding1, cosine similarity1), (centroid_embedding2, cosine similarity2), (centroid_embedding3, cosine similarity3))]
    note that the video embedding corresponds to vidquery is NOT returned.
    '''

    #creates the centroid ndarray of dimension ncentroids * 2048
    centroids = np.array([centroid for centroid, _ in centroid_categories])
    print("Centroids shape:", centroids.shape)
    #since we are going to use l2distance for similarity, the input needs to be l2 normalized
    vidquery = vidquery / np.linalg.norm(vidquery, axis=1, keepdims=True)
    centroids = centroids / np.linalg.norm(centroids, axis=1, keepdims=True)
    print("vidquery shape:", vidquery.shape)

    #create an index for the centroids, not the vidquery
    centroid_index = faiss.IndexFlatL2(centroids.shape[1])
    print(centroid_index.is_trained)
    centroid_index.add(centroids)
    dist, ind = centroid_index.search(vidquery, k) # (squared)l2distance, and  index for each query

    #convert distance to cosine similarity since the vectors are l2 normalized
    cossim = 1 - dist / 2
    print("cossim shape:", cossim.shape)
    # create a list to hold the results
    results = []
    for i in range(vidquery.shape[0]):
        # for each video in the query, find the most similar centroids
        similar_centroids = []
        for j in range(k):
            similar_centroids.append((centroids[ind[i][j]], cossim[i][j]))
        results.append(tuple(similar_centroids))
    return results

def pca_projection(vects, n_components=3):
    '''
    Projects the input vectors (embeddings) into a n_component dimensional space using PCA.
    args:
        vects (np.ndarray): Input vectors(embeddings and centroids) to project.
        n_components (int): Number of components to keep.
    returns: np.ndarray: The projected vectors.
    Note: this function is implemented using scikit learn PCA because faiss is not working
    '''
    pcamatrix = PCA(n_components=n_components)
    if vects.shape[0] < n_components:
        raise ValueError(f"Number of samples ({vects.shape[0]}) must be >= n_components ({n_components}) for PCA.")
    print('The shape of the input vectors is:', vects.shape)
    print(f'reducing dimensionality from {vects.shape[1]} to {n_components}')
    print("Training PCA...")
    projmatrix = pcamatrix.fit_transform(vects)
    print("PCA training completed.")
    
    print('The shape of the projected vectors is:', projmatrix.shape)
    return projmatrix
    

def visualize_embeddings_centroids_pca(vidembed, centroids):
    '''
    Visualize the 3D PCA Projection of the video embeddings and centroid vectors with matplotlib
    Args:
    vidembed : np.ndarray with shape (nb, 2048) containing video embedding vectors
    centroids : np.ndarray with shape (ncentroids, 2048) containing centroid vectors
    '''

    allembed = np.concatenate([vidembed, centroids], axis=0)
    allproj = pca_projection(allembed, n_components=3)

    #split back (to plot differently)
    vidproj = allproj[:len(vidembed)]
    centproj = allproj[len(vidembed):]
    print("vidproj shape:", vidproj.shape)
    print("centproj shape:", centproj.shape)
    # Assume vidproj (vidembed.shape[0], 3) and centproj (ncentroids, 3)
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

if __name__ == "__main__":
    VIDEO_COLLECTION_NAME = "video_embeddings"
    vidembed = retrieve_all_from_qdrant(VIDEO_COLLECTION_NAME) # retrieve all video embeddings from qdrant
    embed1 = retrieve_single_from_qdrant(VIDEO_COLLECTION_NAME,9274612216458326251) # retrieve a single video embedding from qdrant using point_id
    embed2 = retrieve_single_from_qdrant(VIDEO_COLLECTION_NAME,10693639038944902041) # retrieve a single video embedding from qdrant using point_id
    qembed = np.array([embed1, embed2]) # create a query embedding array with the two retrieved embeddings
    print(qembed.shape)
    print(vidembed.shape)
    centroid_categories = cluster_videos(vidembed, ncentroids=ncentroids, niter=niter, verbose=verbose)
    print("centroid_categories:")
    centroids = np.array([centroid for centroid, _ in centroid_categories])
    print('centroids.shape = ')
    print(centroids.shape)
    for centroid, video in centroid_categories:
        print(f"Centroid: {centroid}, Nearest Video: {video}")

        # categorize the query embedding
        categorized = categorize_video(qembed, centroids, k=3)
        print('shape of categorized:')
        print("len of categorized:", len(categorized))
        print("Categorized Video:")

        for video in categorized:
            print(video)

    print("centroids")
    print(centroids)
    print("running PCA projection on the centroids...")
    pca_proj = pca_projection(centroids, 3)

    print(pca_proj)
    print("PCA projection completed.")
    print("Visualizing embeddings and centroids in 3D PCA projection...")
    visualize_embeddings_centroids_pca(vidembed, centroids)