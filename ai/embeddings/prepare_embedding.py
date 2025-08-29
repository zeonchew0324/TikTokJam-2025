import numpy as np

def attention_pooling(embeddings, weights):
    # Simple attention mechanism
    attention_scores = np.dot(embeddings, np.mean(embeddings, axis=0))
    attention_weights = np.exp(attention_scores) / np.sum(np.exp(attention_scores))
    
    # Combine with segment weights
    final_weights = attention_weights * weights
    final_weights = final_weights / np.sum(final_weights)
    
    return np.average(embeddings, axis=0, weights=final_weights)

def prepare_embedding(video_segments):
    # video_segments is an array that contains all the segments of a single video
    if not video_segments:
        raise ValueError("No video segments provided")
    
    # Extract embeddings
    visual_embeddings = [np.array(s.float_) for s in video_segments if s.embedding_option == 'visual-text']
    audio_embeddings = [np.array(s.float_) for s in video_segments if s.embedding_option == 'audio']

    print(f"Visual embeddings shape: {visual_embeddings.shape}")
    print(f"Audio embeddings shape: {audio_embeddings.shape}")
    
    combined_embeddings = np.array([np.concatenate([v, a]) for v, a in zip(visual_embeddings, audio_embeddings)])
    print(f"Combined embeddings shape: {combined_embeddings.shape}")
    
    # Calculate weights based on method
    no_of_segments = len(video_segments) // 2
    weights = np.ones(no_of_segments) / no_of_segments
    
    aggregated_embedding = attention_pooling(combined_embeddings, weights)
    print(f"Aggregated combined embedding shape: {aggregated_embedding.shape}")
    
    return aggregated_embedding