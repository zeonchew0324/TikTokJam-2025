import numpy as np
from sklearn.decomposition import PCA

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

def project_embeddings_to_3d(vidembed, centroids):
    allembed = np.concatenate([vidembed, centroids], axis=0)
    allproj = pca_projection(allembed, n_components=3)

    #split back (to plot differently)
    vidproj = allproj[:len(vidembed)]
    centproj = allproj[len(vidembed):]
    print("vidproj shape:", vidproj.shape)
    print("centproj shape:", centproj.shape)
    return vidproj, centproj