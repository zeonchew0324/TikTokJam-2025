package com.backend.tier_tok.service;

import com.backend.tier_tok.model.entity.*;
import com.backend.tier_tok.repository.CategoryPoolRepository;
import com.backend.tier_tok.repository.VideoRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Lazy;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

@Service
@Slf4j
public class CategoryPoolService {

    @Autowired
    private CategoryPoolRepository categoryPoolRepository;

    @Autowired
    private VideoRepository videoRepository;

    @Autowired
    @Lazy
    private VideoAnalyticsService videoAnalyticsService;

    // Updates the category pool's total weight based on top 50% engagement scores.
    @Transactional
    public void updateCategoryPoolTotalWeight(Long categoryPoolId) {
        CategoryPoolEntity categoryPoolEntity = categoryPoolRepository.findById(categoryPoolId).orElseThrow();

        List<Double> engagementScores = videoRepository.findVideosByCategoryId(categoryPoolId)
                .stream()
                .map(VideoEntity::getEngagementScore)
                .sorted(Comparator.reverseOrder())
                .toList();

        log.info("Engagement score size: {}", engagementScores.size());

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
        Map<VideoTier, Double> tierThresholds = getTierThresholds(categoryPoolId);

        double top5PercentThreshold = tierThresholds.get(VideoTier.PLATINUM);
        double top20PercentThreshold = tierThresholds.get(VideoTier.GOLD);
        double top50PercentThreshold = tierThresholds.get(VideoTier.SILVER);

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

    public Map<VideoTier, Double> getTierThresholds(Long categoryPoolId) {
        List<Double> engagementScores = videoRepository.findVideosByCategoryId(categoryPoolId)
                .stream()
                .map(VideoEntity::getEngagementScore)
                .sorted(Comparator.reverseOrder())
                .toList();

        log.info("Engagement Scores List Size: {}", engagementScores.size());

        Map<VideoTier, Double> thresholds = new HashMap<>();
        if (!engagementScores.isEmpty()) {
            thresholds.put(VideoTier.PLATINUM, engagementScores.get((int) (engagementScores.size() * 0.05)));
            thresholds.put(VideoTier.GOLD, engagementScores.get((int) (engagementScores.size() * 0.20)));
            thresholds.put(VideoTier.SILVER, engagementScores.get((int) (engagementScores.size() * 0.50)));
            thresholds.put(VideoTier.BRONZE, 0.0);
        }
        return thresholds;
    }

    public double getPercentileRank(Long categoryPoolId, double engagementScore) {
        List<Double> engagementScores = videoRepository.findVideosByCategoryId(categoryPoolId)
                .stream()
                .map(VideoEntity::getEngagementScore)
                .sorted(Comparator.reverseOrder())  // Scores are sorted from highest to lowest
                .toList();

        if (engagementScores.isEmpty()) {
            return 0.0;
        }

        // Binary search to find position
        int position = binarySearchPosition(engagementScores, engagementScore);

        // Calculate percentile (higher position means lower percentile)
        return (position * 100.0) / engagementScores.size();
    }

    /**
     * Find the position where the engagement score would be inserted
     * in the sorted list (sorted in descending order).
     * Returns the number of elements greater than the given score.
     */
    private int binarySearchPosition(List<Double> sortedScores, double targetScore) {
        int left = 0;
        int right = sortedScores.size() - 1;

        // If target is higher than all scores
        if (sortedScores.isEmpty() || targetScore > sortedScores.getFirst()) {
            return 0;
        }

        while (left <= right) {
            int mid = left + (right - left) / 2;
            double midScore = sortedScores.get(mid);

            if (midScore == targetScore) {
                // Find the first occurrence if there are duplicates
                while (mid > 0 && sortedScores.get(mid - 1) == targetScore) {
                    mid--;
                }
                return mid;
            } else if (midScore > targetScore) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }

        return left;
    }

    public void updateVideoTierToWeightAndFundMap(Long categoryPoolId, double categoryPoolFund) {
        CategoryPoolEntity categoryPoolEntity = categoryPoolRepository.getReferenceById(categoryPoolId);

        // Fetch all videos in the category to calculate weights for each tier
        Map<VideoTier, Double> videoTierToWeightMap = videoRepository.findVideosByCategoryId(categoryPoolId)
                .stream()
                .collect(Collectors.groupingBy(
                        video -> getVideoTier(categoryPoolId, video.getEngagementScore()),
                        Collectors.summingDouble(video -> {
                            // Find the correct PoolTier for this video and category
                            double categoryPercentage = video.getPoolTiers().stream()
                                    .filter(pt -> Objects.equals(pt.getCategoryPoolEntity().getId(), categoryPoolId))
                                    .mapToDouble(PoolTier::getCategoryPercentage)
                                    .findFirst()
                                    .orElse(0.0);
                            return Math.log(video.getEngagementScore() * categoryPercentage + 1);
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

    @Transactional
    public void updateVideoTiersForCategoryPool(Long categoryPoolId) {
        // 1. Get all videos associated with the category pool
        List<VideoEntity> videos = videoRepository.findVideosByCategoryId(categoryPoolId);

        log.info("Video for category {} size: {}", categoryPoolId, videos.size());

        // 2. Iterate through each video and its pool tiers to update the video tier
        for (VideoEntity video : videos) {
            for (PoolTier poolTier : video.getPoolTiers()) {
                if (Objects.equals(poolTier.getCategoryPoolEntity().getId(), categoryPoolId)) {
                    // Calculate the score used for tier determination
                    double tierScore = video.getEngagementScore() * poolTier.getCategoryPercentage();

                    // Call the method to get the correct video tier
                    VideoTier newTier = getVideoTier(categoryPoolId, tierScore);

                    // Update the pool tier entity
                    poolTier.setVideoTier(newTier);
                }
            }
        }
        // 3. Save the changes to the videos, which will cascade to pool tiers
        videoRepository.saveAll(videos);
    }
}
