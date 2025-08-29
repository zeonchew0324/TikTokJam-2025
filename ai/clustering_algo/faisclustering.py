print("running Faiss Clustering")

'''
This module is responsible for clustering video embeddings using FAISS.
It will receive vidembed as video embeddings in the form of a 2D numpy array.
vidembed will be nb*2048 dimension where nb is the number of video embeddings
Then it will return an array of centroids. 


'''

import os
import sys
import faiss                   # make faiss available, and gpu can be enabled later
import numpy as np


