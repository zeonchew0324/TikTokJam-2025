from ai.tech_stack.qdrant import retrieve_all_from_qdrant, CENTROID_COLLECTION_NAME, retrieve_video_embedding_by_id, retrieve_category_by_embedding
from ai.tech_stack.faiss_algo import categorize_video

centroid_embeddings = retrieve_all_from_qdrant(CENTROID_COLLECTION_NAME)

def categorize_video_into_3_categories(video_id):
    video_embedding = retrieve_video_embedding_by_id(video_id)
    
    if video_embedding is None:
        print(f"Video ID {video_id} not found.")
        return

    category_embeddings_and_similarity_scores = categorize_video(video_embedding, centroid_embeddings)
    
    results = []
    
    for embedding, score in category_embeddings_and_similarity_scores:
        category = retrieve_category_by_embedding(embedding)
        if category:
            score = round(float(score) * 100, 2)
            print(f"Video ID {video_id} is categorized as {category} with a similarity score of {score}.")
            result = {
                "category": category,
                "similarity_score": score
            }
            results.append(result)
    
    return results