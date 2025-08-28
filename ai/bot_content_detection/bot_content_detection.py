print("Bot content detection initialized.")
'''
This module is responsible for detecting bot-generated content in TikTok videos.
This will receive video embeddings in the form of a 1 * 2048 dimensional numpy embedding arrays.
Then, the similarity between the video embeddings is calculated pairwise using faiss.
after that, the video embeddings are processed and classified to be flagged as potential bot-generated content.

'''
import faiss                   # make faiss available, and gpu can be enabled later
import numpy as np
import os
import sys

print("MAKE SURE YOU ARE READING THE EMBEDDINGS CORRECTLY AND NOT RANDOM FAKE DATA")
print('GIVE THE VIDEO EMBEDDINGS AND QUERY EMBEDDINGS AS FIRST AND SECOND COMMAND LINE ARGUMENTS')
####Command line args, enable when deploying
#vidembed = sys.argv[1] # the embedding vectors will be received as a list of 1 * 2048 dimensional numpy arrays in command line arguments
#vidembed = np.array(eval(vidembed)) # convert the string representation of the list to a numpy array
#qembed = sys.argv[2]
#qembed = np.array(eval(qembed))
####

##fake random data, for testing purposes

# set seed
np.random.seed(42)
vidembed = np.random.rand(100, 2048).astype(np.float32)
qembed = np.random.rand(10, 2048).astype(np.float32)
print(f"Generated fake vidembed shape: {vidembed.shape}")
print(f"Generated fake qembed shape: {qembed.shape}")
print("example video embedding:")
print(vidembed[:10])
print("example query embedding:")
print(qembed[:10])
####

k = 5 #this is the number for nearest neighbors in bot similarity detection



#since we are going to use l2distance for similarity, the input needs to be l2 normalized
vidembed = vidembed / np.linalg.norm(vidembed, axis=1, keepdims=True)

print(f"Received embeddings shape: {vidembed.shape}")
print(f'number of videos: {vidembed.shape[0]}')
#vidembed is the video embeddings array of preexisting video vector embeddings


#now lets do some query


qembed = qembed / np.linalg.norm(qembed, axis=1, keepdims=True)

print(f"Received query embedding shape: {qembed.shape}")

#we need to list out the k most similar videos for each video from query against the vidembed

index = faiss.IndexFlatL2(vidembed.shape[1])   # build the index with the dimension
print(index.is_trained)
index.add(vidembed)                  # add vectors to the index
print(index.ntotal)
dist, ind = index.search(qembed, k)     # (squared)l2distance, and  index for each query


# now we find the 5% most similar video pairs (from vid and query) and report it out to the user
flat_dist = dist.flatten()
flat_ind = ind.flatten()

top_n = int(0.05 * flat_dist.size)

dist_threshold = flat_dist[np.argsort(flat_dist)[:top_n][-1]] # this is the maximum distance for the top 5% most similar videos
flagged_dist = np.where(dist <= dist_threshold, 1, 0) # set distances above the threshold to infinity


# Generate list of (vidembed index, qembed index, distance) tuples for flagged pairs
flagged_pairs = [
    (ind[iq, iv], iq, dist[iq, iv])
    for iq in range(flagged_dist.shape[0])
    for iv in range(flagged_dist.shape[1])
    if flagged_dist[iq, iv] == 1
]
print("Flagged pairs (vidembed index, qembed index, distance):", flagged_pairs)


