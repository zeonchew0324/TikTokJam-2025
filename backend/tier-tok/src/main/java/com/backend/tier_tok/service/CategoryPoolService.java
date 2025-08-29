package com.backend.tier_tok.service;

import com.backend.tier_tok.model.entity.*;
import com.backend.tier_tok.repository.CategoryPoolRepository;
import com.backend.tier_tok.repository.VideoRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class CategoryPoolService {

    @Autowired
    private CategoryPoolRepository categoryPoolRepository;

    @Autowired
    private VideoRepository videoRepository;

    @Autowired
    private VideoAnalyticsService videoAnalyticsService;

    // Updates the category pool's total weight based on top 50% engagement scores.
    public void updateCategoryPoolTotalWeight(Long categoryPoolId) {
        CategoryPoolEntity categoryPoolEntity = categoryPoolRepository.getReferenceById(categoryPoolId);

        List<Double> engagementScores = videoRepository.findByPoolTiers_CategoryPoolEntity_Id(categoryPoolId)
                .stream()
                .map(videoAnalyticsService::getEngagementScore)
                .sorted(Comparator.reverseOrder())
                .toList();

        int top50PercentCount = (int) Math.ceil(engagementScores.size() * 0.5);
        double totalWeight = engagementScores.stream()
                .limit(top50PercentCount)
                .mapToDouble(Double::doubleValue)
                .sum();

        categoryPoolEntity.setTotalCategoryPoolWeight(totalWeight);
        categoryPoolRepository.save(categoryPoolEntity);
    }

    // Determines the video tier based on its engagement score and category thresholds.
    public VideoTier getVideoTier(Long categoryPoolId, double videoEngagementScore) {
        // This is a placeholder; in a real-world scenario, the thresholds should be pre-calculated
        // and stored, or a more efficient calculation method would be used.
        // For demonstration purposes, we will fetch all scores to calculate thresholds.
        List<Double> engagementScores = videoRepository.findByPoolTiers_CategoryPoolEntity_Id(categoryPoolId)
                .stream()
                .map(videoAnalyticsService::getEngagementScore)
                .sorted(Comparator.reverseOrder())
                .toList();

        double top5PercentThreshold = !engagementScores.isEmpty() ? engagementScores.get((int) (engagementScores.size() * 0.05)) : 0;
        double top20PercentThreshold = !engagementScores.isEmpty() ? engagementScores.get((int) (engagementScores.size() * 0.20)) : 0;
        double top50PercentThreshold = !engagementScores.isEmpty() ? engagementScores.get((int) (engagementScores.size() * 0.50)) : 0;

        if (videoEngagementScore >= top5PercentThreshold) {
            return VideoTier.PLATINUM;
        } else if (videoEngagementScore >= top20PercentThreshold) {
            return VideoTier.GOLD;
        } else if (videoEngagementScore >= top50PercentThreshold) {
            return VideoTier.SILVER;
        } else {
            return VideoTier.BRONZE;
        }
    }

    public void updateVideoTierToWeightAndFundMap(Long categoryPoolId, double categoryPoolFund) {
        CategoryPoolEntity categoryPoolEntity = categoryPoolRepository.getReferenceById(categoryPoolId);

        // Fetch all videos in the category to calculate weights for each tier
        Map<VideoTier, Double> videoTierToWeightMap = videoRepository.findByPoolTiers_CategoryPoolEntity_Id(categoryPoolId)
                .stream()
                .collect(Collectors.groupingBy(
                        video -> getVideoTier(categoryPoolId, videoAnalyticsService.getEngagementScore(video)),
                        Collectors.summingDouble(video -> {
                            // Find the correct PoolTier for this video and category
                            double categoryPercentage = video.getPoolTiers().stream()
                                    .filter(pt -> pt.getCategoryPoolEntity().getId() == categoryPoolId)
                                    .mapToDouble(PoolTier::getCategoryPercentage)
                                    .findFirst()
                                    .orElse(0.0);
                            return Math.log(videoAnalyticsService.getEngagementScore(video) * categoryPercentage + 1);
                        })
                ));

        categoryPoolEntity.setVideoTierToWeightMap(videoTierToWeightMap);
        categoryPoolEntity.setTotalCategoryPoolFund(categoryPoolFund);

        // Distribute the category fund to each tier
        double totalTierWeight = videoTierToWeightMap.values().stream().mapToDouble(Double::doubleValue).sum();

        Map<VideoTier, Double> videoTierToFundMap = videoTierToWeightMap.entrySet().stream()
                .collect(Collectors.toMap(
                        Map.Entry::getKey,
                        entry -> (entry.getValue() / totalTierWeight) * categoryPoolFund
                ));

        categoryPoolEntity.setVideoTierToFundMap(videoTierToFundMap);
        categoryPoolRepository.save(categoryPoolEntity);
    }
}
