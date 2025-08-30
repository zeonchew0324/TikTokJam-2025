from ai.tech_stack.qdrant import retrieve_all_from_qdrant, CENTROID_COLLECTION_NAME, retrieve_video_embedding_by_id, retrieve_category_by_embedding
from ai.tech_stack.faiss_algo import categorize_video

def categorize_video_into_3_categories(video_id):
    video_embedding = retrieve_video_embedding_by_id(video_id)
    centroid_embeddings = retrieve_all_from_qdrant(CENTROID_COLLECTION_NAME)
    
    if video_embedding is None:
        print(f"Video ID {video_id} not found.")
        return
    
    if centroid_embeddings is None:
        print("No centroids found.")
        return

    category_embeddings_and_similarity_scores = categorize_video(video_embedding, centroid_embeddings)
    
    total_score = sum(float(score) for _, score in category_embeddings_and_similarity_scores)
    
    if total_score == 0:
        print("Total similarity score is zero, cannot compute percentages.")
        return
    
    results = []
    
    for embedding, score in category_embeddings_and_similarity_scores:
        category = retrieve_category_by_embedding(embedding)
        if category:
            percentage = (float(score) / total_score) * 100
            percentage = round(percentage, 2)
            print(f"Video ID {video_id} is categorized as {category} with a percentage of {percentage}.")
            result = {
                "category": category,
                "percentage": percentage
            }
            results.append(result)
    
    return results

categorize_video_into_3_categories("1c747767_tiktok_7522090387679268102_video.mp4")