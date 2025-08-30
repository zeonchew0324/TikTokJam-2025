package com.backend.tier_tok.service;

import com.backend.tier_tok.model.DTO.PayoutDTO;
import com.backend.tier_tok.model.DTO.VideoAnalyticsResponseDTO;
import com.backend.tier_tok.model.entity.PoolTier;
import com.backend.tier_tok.model.entity.VideoEntity;
import com.backend.tier_tok.model.entity.VideoTier;
import com.backend.tier_tok.repository.CategoryPoolRepository;
import com.backend.tier_tok.repository.VideoRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Lazy;
import org.springframework.stereotype.Repository;
import org.springframework.stereotype.Service;
import org.springframework.http.ResponseEntity;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Map;

@Service
@Slf4j
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

    @Autowired
    private VideoRepository videoRepository;

    @Autowired
    private CategoryPoolRepository categoryPoolRepository;

    private static final double ALPHA = 0.1;
    private static final double BETA = 0.4;
    private static final double GAMMA = 0.5;
    private static final double LAMBDA = 0.4;
    private static final int MAX_BONUS = 3;
    private static final int k = 500;

    @Value("${ai.server.base.url}")
    private String base_url;

    @Transactional
    public double getEngagementScore(VideoEntity videoEntity) {
        double watchTimeRatio = videoEntity.getWatchTime() / videoEntity.getTotalViewCount() * videoEntity.getDuration();
        double commentRatio = (double) videoEntity.getCommentCount() / videoEntity.getLikeCount();
        double recentViewCount = videoEntity.getTotalViewCount() - videoEntity.getPastMonthsViewCount();

        long numberOfMonths = ChronoUnit.MONTHS.between(
                LocalDateTime.now().toLocalDate(),
                videoEntity.getCreatedAt().toLocalDate()
        );

        double viewCount = videoEntity.getPastMonthsViewCount()
                * Math.exp(-LAMBDA * numberOfMonths) + recentViewCount;

        double engagementScore = ALPHA * Math.log(viewCount + 1) + BETA * watchTimeRatio + GAMMA * commentRatio;
        log.info("Got engagement score from the function itself: {}", engagementScore);

        // TODO: Add content evaluation Score in engagementScore
        // GET FROM API REQUEST FROM AI SERVER
        HttpClient client = HttpClient.newHttpClient();
        String apiUrl = base_url + "/admin/evaluate-video?video_id=" + videoEntity.getVideo_id();

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(apiUrl)) // Replace with your target URL
                .GET() // Explicitly set the method to GET (it's the default if not specified)
                .build();

        try {
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

            // Process the response
            log.info("Status Code: {}", response.statusCode());
            log.info("Response Body: {}", response.body());
            if (response.statusCode() == 200) {
                // Parse the JSON response to extract quality_score
                ObjectMapper objectMapper = new ObjectMapper();
                JsonNode jsonNode = objectMapper.readTree(response.body());
                double videoContentQualityScore = jsonNode.get("quality_score").asDouble();

                log.info("Extracted quality score: {}", videoContentQualityScore);
                double qualityMultiplier = 1 + videoContentQualityScore * MAX_BONUS * Math.pow(Math.E, -engagementScore / k);

                videoEntity.setEngagementScore(engagementScore * qualityMultiplier);
            } else {
                log.error("Error response from AI server: {}", response.statusCode());

                // no multiplier
                videoEntity.setEngagementScore(engagementScore);
            }
            videoRepository.save(videoEntity);
            return videoService.getVideoById(videoEntity.getVideo_id()).getEngagementScore();

        } catch (Exception e) {
            log.error("Error calling AI Server");
            return 0.0;
        }

    }

    private double calculateRank(VideoEntity videoEntity) {
        double engagementScore = videoEntity.getEngagementScore();

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
        double currentScore = videoEntity.getEngagementScore();
        double minScoreNeeded = Double.MAX_VALUE;

        // For each category the video belongs to
        for (PoolTier poolTier : videoEntity.getPoolTiers()) {
            Long categoryId = poolTier.getCategoryPoolEntity().getId();
            VideoTier currentTier = poolTier.getVideoTier() == null ? VideoTier.BRONZE : poolTier.getVideoTier();

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

    public VideoAnalyticsResponseDTO getVideoAnalytics(String videoId, boolean isRefresh) {
        log.info("Getting video analytics for videoId: {}", videoId);
        VideoEntity videoEntity = videoService.getVideoById(videoId);

        if (isRefresh) {
            double engagementScore = getEngagementScore(videoEntity);
            log.info("Engagement Score for Video {}: {}", videoEntity.getVideo_id(), engagementScore);

            // the video pool tier might need to process first
            videoService.processVideoPoolTiers(videoId, engagementScore);

//            categoryPoolRepository.findAll().forEach(
//                    categoryPoolEntity -> categoryPoolService
//                            .updateVideoTiersForCategoryPool(categoryPoolEntity.getId()));

            log.info("Successfully processed video tier for video");
            videoEntity.getPoolTiers().forEach(poolTier ->
                    log.info("Pool Tier Category: {}, Percentage: {}, Tier: {}",
                            poolTier.getCategoryPoolEntity().getName(),
                            poolTier.getCategoryPercentage(),
                            poolTier.getVideoTier()));
        }

        return VideoAnalyticsResponseDTO.builder()
                .videoId(videoEntity.getVideo_id())
                .caption(videoEntity.getCaption())
                .watchTime(videoEntity.getWatchTime())
                .commentCount(videoEntity.getCommentCount())
                .likeCount(videoEntity.getLikeCount())
                .pastMonthsTotalViewCount(videoEntity.getPastMonthsViewCount())
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
                                    .videoPayout(videoPayoutCalculatorService.getVideoPayout(videoEntity, videoEntity.getEngagementScore()))
                                    .videoTier(poolTier.getVideoTier())
                                    .engagementScore(videoEntity.getEngagementScore())
                                    .build()
                                ).toList()
                ).build();
    }
}