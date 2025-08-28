import numpy as np

def aggregate_segments(video_segments):
    # video_segments is an array that contains all the segments of a single video
    if not video_segments:
        raise ValueError("No video segments provided")

    # Extract embeddings
    visual_embeddings = np.array([s.float_ for s in video_segments if s.embedding_option == 'visual-text'])
    audio_embeddings = np.array([s.float_ for s in video_segments if s.embedding_option == 'audio'])

    print(f"Visual embeddings shape: {visual_embeddings.shape}")
    print(f"Audio embeddings shape: {audio_embeddings.shape}")
    
    # Calculate weights based on method
    no_of_segments = len(video_segments) // 2
    weights = np.ones(no_of_segments) / no_of_segments
    
    agg_visual_embedding = attention_pooling(visual_embeddings, weights)
    agg_audio_embedding = attention_pooling(audio_embeddings, weights)

    print(f"Aggregated visual embedding shape: {agg_visual_embedding.shape}")
    print(f"Aggregated audio embedding shape: {agg_audio_embedding.shape}")
    
    return agg_visual_embedding, agg_audio_embedding

def attention_pooling(embeddings, weights):
    # Simple attention mechanism
    attention_scores = np.dot(embeddings, np.mean(embeddings, axis=0))
    attention_weights = np.exp(attention_scores) / np.sum(np.exp(attention_scores))
    
    # Combine with segment weights
    final_weights = attention_weights * weights
    final_weights = final_weights / np.sum(final_weights)
    
    return np.average(embeddings, axis=0, weights=final_weights)

def combine_modalities(visual_embedding, audio_embedding):
    # Contatenate visual embedding and audio_embedding into one combined_embedding
    concatenated_embedding = np.concatenate([visual_embedding, audio_embedding])
    
    print(f"Concatenated embedding shape: {concatenated_embedding.shape}")

    return concatenated_embedding / np.linalg.norm(concatenated_embedding)

def prepare_embedding(video_segments):
    # Aggregate segments for this video
    aggregated_embeddings = aggregate_segments(video_segments)
    
    # Combine modalities
    combined_embedding = combine_modalities(aggregated_embeddings[0], aggregated_embeddings[1])
    
    return combined_embedding