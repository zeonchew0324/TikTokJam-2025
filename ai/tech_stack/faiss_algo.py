print("running Faiss Clustering")

'''
This module is responsible for clustering video embeddings using FAISS.
It will receive vidembed as video embeddings in the form of a 2D numpy array.
vidembed will be nb*2048 dimension where nb is the number of video embeddings
Then it will return an array of centroids. 


'''




import faiss                   # make faiss available, and gpu can be enabled later
import numpy as np
from ai.tech_stack.qdrant import retrieve_all_from_qdrant, CENTROID_COLLECTION_NAME, retrieve_single_from_qdrant
ncentroids = 4 # the number of centroids

niter = 20
verbose = True

def cluster_videos(vidembed, ncentroids=4, niter=20, verbose=True):
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
    print("Centroids shape:", centroids.shape)
    #since we are going to use l2distance for similarity, the input needs to be l2 normalized
    vidquery = vidquery.reshape(-1, 2048)
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
    similar_centroids = []
    for j in range(k):
        similar_centroids.append((centroids[ind[0][j]], cossim[0][j]))
    return similar_centroids