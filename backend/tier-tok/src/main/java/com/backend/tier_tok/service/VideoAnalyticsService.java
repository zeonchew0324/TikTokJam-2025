package com.backend.tier_tok.service;

import com.backend.tier_tok.model.DTO.PayoutDTO;
import com.backend.tier_tok.model.DTO.VideoAnalyticsResponseDTO;
import com.backend.tier_tok.model.entity.VideoEntity;
import com.backend.tier_tok.repository.VideoRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;

@Service
public class VideoAnalyticsService {

    @Autowired
    private VideoRepository videoRepository;

    @Autowired
    private VideoPayoutCalculatorService videoPayoutCalculatorService;

    private static final double ALPHA = 0.1;
    private static final double BETA = 0.4;
    private static final double GAMMA = 0.5;
    private static final double LAMBDA = 0.4;

    public double getEngagementScore(VideoEntity videoEntity) {
        double watchTimeRatio = (double) videoEntity.getWatchTime() / videoEntity.getTotalViewCount() * videoEntity.getDuration();
        double commentRatio = (double) videoEntity.getCommentCount() / videoEntity.getLikeCount();
        double recentViewCount = videoEntity.getTotalViewCount() - videoEntity.getPastMonthsTotalViewCount();

        long numberOfMonths = ChronoUnit.MONTHS.between(
                LocalDateTime.now().toLocalDate(),
                videoEntity.getCreatedAt().toLocalDate()
        );

        double viewCount = videoEntity.getPastMonthsTotalViewCount()
                * Math.exp(-LAMBDA * numberOfMonths) + recentViewCount;

        return ALPHA * Math.log(viewCount + 1) + BETA * watchTimeRatio + GAMMA * commentRatio;
    }

    public VideoAnalyticsResponseDTO getVideoAnalytics(String videoId) {
        VideoEntity videoEntity = videoRepository.getReferenceById(videoId);

        if (videoEntity == null) {
            throw new RuntimeException("Error get video analytics");
        }
        double engagementScore = getEngagementScore(videoEntity);

        return VideoAnalyticsResponseDTO.builder()
                .videoId(videoEntity.getId())
                .caption(videoEntity.getCaption())
                .watchTime(videoEntity.getWatchTime())
                .commentCount(videoEntity.getCommentCount())
                .likeCount(videoEntity.getLikeCount())
                .pastMonthsTotalViewCount(videoEntity.getPastMonthsTotalViewCount())
                .totalViewCount(videoEntity.getTotalViewCount())
                .creator(videoEntity.getCreator())
                .payoutDTOList(videoEntity.getPoolTiers().stream().map(poolTier -> PayoutDTO.builder()
                        .categoryName(poolTier.getCategoryPoolEntity().getName())
                        .percentage(poolTier.getCategoryPercentage())
                        .videoPayout(videoPayoutCalculatorService.getVideoPayout(videoEntity, engagementScore))
                        .videoTier(poolTier.getVideoTier())
                        .engagementScore(engagementScore)
                        .build()).toList())
                .build();
    }
}