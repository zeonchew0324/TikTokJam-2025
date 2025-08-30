print("running Faiss Clustering")

'''
This module is responsible for clustering video embeddings using FAISS.
It will receive vidembed as video embeddings in the form of a 2D numpy array.
vidembed will be nb*2048 dimension where nb is the number of video embeddings
Then it will return an array of centroids. 


'''
import faiss                   # make faiss available, and gpu can be enabled later
import numpy as np
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


def categorize_video(vidquery, centroid_categories, k=3):
    '''
    for each video in vidquery, find k most similar centroids to it, where centroid is given by centroid_categories
    Args:
        vidquery (np.ndarray): 2D numpy array of shape (nb, 2048) containing video query embeddings.
        centroid_categories (List[Tuple[np.ndarray, np.ndarray]]): List of tuples, each containing a centroid embedding and its nearest video embedding.
    Returns: List[Tuple[video_embedding, (centroid_embedding1,cosine similarity1), (centroid_embedding2, cosine similarity2), (centroid_embedding3, cosine similarity3)]]
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
        results.append((vidquery[i], *similar_centroids))
    return results


if __name__ == "__main__":
    vidembed = retrieve_all_from_qdrant() # retrieve all video embeddings from qdrant
    embed1 = retrieve_single_from_qdrant(9274612216458326251) # retrieve a single video embedding from qdrant using point_id
    embed2 = retrieve_single_from_qdrant(10693639038944902041) # retrieve a single video embedding from qdrant using point_id
    qembed = np.array([embed1, embed2]) # create a query embedding array with the two retrieved embeddings
    print(qembed.shape)
    print(vidembed.shape)
    centroid_categories = cluster_videos(vidembed, ncentroids=ncentroids, niter=niter, verbose=verbose)
    print("centroid_categories:")
    for centroid, video in centroid_categories:
        print(f"Centroid: {centroid}, Nearest Video: {video}")

        # categorize the query embedding
        categorized = categorize_video(qembed, centroid_categories)
        print("Categorized Video:")
        for video in categorized:
            print(video)