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

def faissclustering(vidembed, ncentroids=100, niter=20, verbose=True):
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

if __name__ == "__main__":
    vidembed = retrieve_all_from_qdrant() # retrieve all video embeddings from qdrant
    embed1 = retrieve_single_from_qdrant(9274612216458326251) # retrieve a single video embedding from qdrant using point_id
    embed2 = retrieve_single_from_qdrant(10693639038944902041) # retrieve a single video embedding from qdrant using point_id
    qembed = np.array([embed1, embed2]) # create a query embedding array with the two retrieved embeddings
    print(qembed.shape)
    print(vidembed.shape)
    centroid_categories = faissclustering(vidembed, ncentroids=ncentroids, niter=niter, verbose=verbose)
    print("centroid_categories:")
    for centroid, video in centroid_categories:
        print(f"Centroid: {centroid}, Nearest Video: {video}")