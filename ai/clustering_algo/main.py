import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_distances, euclidean_distances
from typing import List, Dict, Tuple, Optional
import logging

class VideoCategoryClusterer:
    """
    A clustering algorithm for video embeddings that maintains stable centroids
    and provides soft classification with engagement score distribution.
    """
    
    def __init__(self, n_categories: int, distance_metric: str = 'cosine', random_state: int = 42):
        """
        Initialize the video category clusterer.
        
        Args:
            n_categories: Number of categories (centroids) to create
            distance_metric: Distance metric to use ('cosine' or 'euclidean')
            random_state: Random state for reproducibility
        """
        self.n_categories = n_categories
        self.distance_metric = distance_metric
        self.random_state = random_state
        self.centroids = None
        self.is_fitted = False
        self.category_names = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def initial_clustering(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Perform initial k-means clustering to establish centroids.
        
        Args:
            embeddings: Array of video embeddings, shape (n_videos, embedding_dim)
            
        Returns:
            Initial cluster assignments
        """
        self.logger.info(f"Performing initial clustering with {self.n_categories} categories")
        
        kmeans = KMeans(
            n_clusters=self.n_categories,
            random_state=self.random_state,
            n_init=10,
            max_iter=300
        )
        
        cluster_assignments = kmeans.fit_predict(embeddings)
        self.centroids = kmeans.cluster_centers_
        self.is_fitted = True
        
        return cluster_assignments
    
    def _calculate_distances(self, embeddings: np.ndarray, centroids: np.ndarray) -> np.ndarray:
        """Calculate distances between embeddings and centroids."""
        if self.distance_metric == 'cosine':
            return cosine_distances(embeddings, centroids)
        elif self.distance_metric == 'euclidean':
            return euclidean_distances(embeddings, centroids)
        else:
            raise ValueError("Distance metric must be 'cosine' or 'euclidean'")
    
    def recalibrate_centroids(self, embeddings: np.ndarray, cluster_assignments: np.ndarray):
        """
        Recalibrate centroids based on current cluster assignments.
        This is called daily to update centroids while keeping them stable.
        
        Args:
            embeddings: Current video embeddings
            cluster_assignments: Current cluster assignments
        """
        if not self.is_fitted:
            raise ValueError("Must perform initial clustering first")
        
        self.logger.info("Recalibrating centroids")
        
        # Update centroids based on current assignments
        new_centroids = np.zeros_like(self.centroids)
        
        for category_id in range(self.n_categories):
            mask = cluster_assignments == category_id
            if np.sum(mask) > 0:
                new_centroids[category_id] = np.mean(embeddings[mask], axis=0)
            else:
                # If no videos assigned to this category, keep the old centroid
                new_centroids[category_id] = self.centroids[category_id]
        
        self.centroids = new_centroids
    
    def classify_video(self, video_embedding: np.ndarray, top_k: int = 3) -> Dict:
        """
        Classify a single video and return category percentages for top-k closest categories.
        
        Args:
            video_embedding: Single video embedding, shape (embedding_dim,)
            top_k: Number of closest categories to consider
            
        Returns:
            Dictionary with classification results including percentages and distances
        """
        if not self.is_fitted:
            raise ValueError("Must perform initial clustering first")
        
        # Reshape if needed
        if video_embedding.ndim == 1:
            video_embedding = video_embedding.reshape(1, -1)
        
        # Calculate distances to all centroids
        distances = self._calculate_distances(video_embedding, self.centroids).flatten()
        
        # Get top-k closest categories
        closest_categories = np.argsort(distances)[:top_k]
        closest_distances = distances[closest_categories]
        
        # Convert distances to similarity scores (inverse of distance)
        # Add small epsilon to avoid division by zero
        epsilon = 1e-8
        similarities = 1 / (closest_distances + epsilon)
        
        # Convert to percentages
        total_similarity = np.sum(similarities)
        percentages = (similarities / total_similarity) * 100
        
        return {
            'category_ids': closest_categories.tolist(),
            'distances': closest_distances.tolist(),
            'percentages': percentages.tolist(),
            'primary_category': closest_categories[0],
            'primary_percentage': percentages[0]
        }
    
    def distribute_engagement_score(self, video_embedding: np.ndarray, 
                                  engagement_score: float, top_k: int = 3) -> Dict:
        """
        Distribute engagement score across categories based on video's affinity to each category.
        
        Args:
            video_embedding: Single video embedding
            engagement_score: Engagement score to distribute
            top_k: Number of categories to distribute score across
            
        Returns:
            Dictionary with engagement score distribution
        """
        classification_result = self.classify_video(video_embedding, top_k)
        
        engagement_distribution = {}
        for i, category_id in enumerate(classification_result['category_ids']):
            percentage = classification_result['percentages'][i]
            distributed_score = engagement_score * (percentage / 100)
            engagement_distribution[f'category_{category_id}'] = distributed_score
        
        return {
            'total_engagement_score': engagement_score,
            'distribution': engagement_distribution,
            'classification_info': classification_result
        }
    
    def batch_classify(self, embeddings: np.ndarray, top_k: int = 3) -> List[Dict]:
        """
        Classify multiple videos at once.
        
        Args:
            embeddings: Array of video embeddings, shape (n_videos, embedding_dim)
            top_k: Number of closest categories to consider for each video
            
        Returns:
            List of classification results for each video
        """
        if not self.is_fitted:
            raise ValueError("Must perform initial clustering first")
        
        results = []
        for i, embedding in enumerate(embeddings):
            result = self.classify_video(embedding, top_k)
            result['video_index'] = i
            results.append(result)
        
        return results
    
    def get_category_statistics(self, embeddings: np.ndarray, 
                              engagement_scores: Optional[np.ndarray] = None) -> pd.DataFrame:
        """
        Get statistics for each category including video counts and average engagement.
        
        Args:
            embeddings: All video embeddings
            engagement_scores: Optional engagement scores for each video
            
        Returns:
            DataFrame with category statistics
        """
        if not self.is_fitted:
            raise ValueError("Must perform initial clustering first")
        
        # Get primary category assignments
        classifications = self.batch_classify(embeddings, top_k=1)
        primary_categories = [result['primary_category'] for result in classifications]
        
        stats = []
        for category_id in range(self.n_categories):
            category_mask = np.array(primary_categories) == category_id
            video_count = np.sum(category_mask)
            
            stat_dict = {
                'category_id': category_id,
                'video_count': video_count,
                'percentage_of_total': (video_count / len(embeddings)) * 100
            }
            
            if engagement_scores is not None:
                category_engagement = engagement_scores[category_mask]
                stat_dict.update({
                    'avg_engagement': np.mean(category_engagement) if len(category_engagement) > 0 else 0,
                    'total_engagement': np.sum(category_engagement),
                    'engagement_std': np.std(category_engagement) if len(category_engagement) > 0 else 0
                })
            
            stats.append(stat_dict)
        
        return pd.DataFrame(stats)
    
    def save_centroids(self, filepath: str):
        """Save centroids to a file."""
        if not self.is_fitted:
            raise ValueError("No centroids to save. Perform clustering first.")
        
        np.save(filepath, self.centroids)
        self.logger.info(f"Centroids saved to {filepath}")
    
    def load_centroids(self, filepath: str):
        """Load centroids from a file."""
        self.centroids = np.load(filepath)
        self.is_fitted = True
        self.n_categories = len(self.centroids)
        self.logger.info(f"Centroids loaded from {filepath}")


# Example usage and testing
def example_usage():
    """
    Example of how to use the VideoCategoryClusterer
    """
    
    # Generate sample video embeddings (replace with your Qdrant embeddings)
    np.random.seed(42)
    n_videos = 1000
    embedding_dim = 512
    embeddings = np.random.rand(n_videos, embedding_dim)
    engagement_scores = np.random.rand(n_videos) * 100  # Random engagement scores
    
    # Initialize clusterer
    clusterer = VideoCategoryClusterer(n_categories=10, distance_metric='cosine')
    
    # Step 1: Initial clustering to establish centroids
    initial_assignments = clusterer.initial_clustering(embeddings)
    print(f"Initial clustering completed. Categories: {len(np.unique(initial_assignments))}")
    
    # Step 2: Daily recalibration (in production, this would be done daily)
    clusterer.recalibrate_centroids(embeddings, initial_assignments)
    print("Centroids recalibrated")
    
    # Step 3: Classify new videos
    new_video_embedding = np.random.rand(embedding_dim)
    classification = clusterer.classify_video(new_video_embedding, top_k=3)
    print(f"New video classification: {classification}")
    
    # Step 4: Distribute engagement score
    engagement_distribution = clusterer.distribute_engagement_score(
        new_video_embedding, engagement_score=85.5, top_k=3
    )
    print(f"Engagement distribution: {engagement_distribution}")
    
    # Step 5: Get category statistics
    stats = clusterer.get_category_statistics(embeddings, engagement_scores)
    print("\nCategory Statistics:")
    print(stats)
    
    # Step 6: Save centroids for persistence
    clusterer.save_centroids("ai/clustering_algo/video_centroids.npy")
    
    return clusterer, embeddings, engagement_scores


if __name__ == "__main__":
    clusterer, embeddings, scores = example_usage()