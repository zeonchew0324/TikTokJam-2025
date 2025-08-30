package com.backend.tier_tok.service;

import com.backend.tier_tok.model.DTO.PayoutDTO;
import com.backend.tier_tok.model.DTO.VideoAnalyticsResponseDTO;
import com.backend.tier_tok.model.entity.PoolTier;
import com.backend.tier_tok.model.entity.VideoEntity;
import com.backend.tier_tok.model.entity.VideoTier;
import com.backend.tier_tok.repository.VideoRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Lazy;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Map;

@Service
public class VideoAnalyticsService {

//    @Autowired
//    private VideoRepository videoRepository;

    @Autowired
    private VideoPayoutCalculatorService videoPayoutCalculatorService;

    @Autowired
    @Lazy
    private VideoService videoService;

    @Autowired
    @Lazy
    private CategoryPoolService categoryPoolService;

    private static final double ALPHA = 0.1;
    private static final double BETA = 0.4;
    private static final double GAMMA = 0.5;
    private static final double LAMBDA = 0.4;

    public double getEngagementScore(VideoEntity videoEntity) {
        double watchTimeRatio = videoEntity.getWatchTime() / videoEntity.getTotalViewCount() * videoEntity.getDuration();
        double commentRatio = (double) videoEntity.getCommentCount() / videoEntity.getLikeCount();
        double recentViewCount = videoEntity.getTotalViewCount() - videoEntity.getPastMonthsTotalViewCount();

        long numberOfMonths = ChronoUnit.MONTHS.between(
                LocalDateTime.now().toLocalDate(),
                videoEntity.getCreatedAt().toLocalDate()
        );

        double viewCount = videoEntity.getPastMonthsTotalViewCount()
                * Math.exp(-LAMBDA * numberOfMonths) + recentViewCount;

        return ALPHA * Math.log(viewCount + 1) + BETA * watchTimeRatio + GAMMA * commentRatio;

        // TODO: Add content evaluation Score in engagementScore
    }

    private double calculateRank(VideoEntity videoEntity) {
        double engagementScore = getEngagementScore(videoEntity);

        // Find the video's percentile rank in each category it belongs to
        return videoEntity.getPoolTiers().stream()
                .mapToDouble(poolTier -> {
                    Long categoryId = poolTier.getCategoryPoolEntity().getId();
                    return categoryPoolService.getPercentileRank(categoryId, engagementScore);
                })
                .max()
                .orElse(0.0); // Return the highest percentile rank
    }

    private double calculateEngagementScoreToNextTier(VideoEntity videoEntity) {
        double currentScore = getEngagementScore(videoEntity);
        double minScoreNeeded = Double.MAX_VALUE;

        // For each category the video belongs to
        for (PoolTier poolTier : videoEntity.getPoolTiers()) {
            Long categoryId = poolTier.getCategoryPoolEntity().getId();
            VideoTier currentTier = poolTier.getVideoTier();

            // Get all tier thresholds for this category
            Map<VideoTier, Double> thresholds = categoryPoolService.getTierThresholds(categoryId);

            // Find the next tier's threshold
            double nextThreshold;
            switch (currentTier) {
                case BRONZE -> nextThreshold = thresholds.get(VideoTier.SILVER);
                case SILVER -> nextThreshold = thresholds.get(VideoTier.GOLD);
                case GOLD -> nextThreshold = thresholds.get(VideoTier.PLATINUM);
                default -> nextThreshold = Double.MAX_VALUE;
            }

            if (nextThreshold > currentScore && nextThreshold < minScoreNeeded) {
                minScoreNeeded = nextThreshold;
            }
        }

        return minScoreNeeded == Double.MAX_VALUE ? 0 : minScoreNeeded - currentScore;
    }

    public VideoAnalyticsResponseDTO getVideoAnalytics(String videoId) {
        VideoEntity videoEntity = videoService.getVideoById(videoId);

        double engagementScore = getEngagementScore(videoEntity);

        // the video pool tier might need to process first
        videoService.processVideoPoolTiers(videoId, engagementScore);

        return VideoAnalyticsResponseDTO.builder()
                .videoId(videoEntity.getId())
                .caption(videoEntity.getCaption())
                .watchTime(videoEntity.getWatchTime())
                .commentCount(videoEntity.getCommentCount())
                .likeCount(videoEntity.getLikeCount())
                .pastMonthsTotalViewCount(videoEntity.getPastMonthsTotalViewCount())
                .totalViewCount(videoEntity.getTotalViewCount())
                .videoUrl(videoEntity.getVideoUrl())
                .rank(calculateRank(videoEntity))
                .engagementScoreToNextTier(calculateEngagementScoreToNextTier(videoEntity))
                .creator(videoEntity.getCreator())
                .payoutDTOList(
                        videoEntity.getPoolTiers().stream().map(
                                poolTier -> PayoutDTO.builder()
                                    .categoryName(poolTier.getCategoryPoolEntity().getName())
                                    .percentage(poolTier.getCategoryPercentage())
                                    .videoPayout(videoPayoutCalculatorService.getVideoPayout(videoEntity, engagementScore))
                                    .videoTier(poolTier.getVideoTier())
                                    .engagementScore(engagementScore)
                                    .build()
                                ).toList()
                ).build();
    }
}