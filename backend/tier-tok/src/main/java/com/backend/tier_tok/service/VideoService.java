package com.backend.tier_tok.service;

import com.backend.tier_tok.model.entity.PoolTier;
import com.backend.tier_tok.model.entity.VideoEntity;
import com.backend.tier_tok.model.entity.VideoTier;
import com.backend.tier_tok.repository.VideoRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@Slf4j
public class VideoService {
    @Autowired
    private VideoRepository videoRepository;

    @Autowired
    private VideoAnalyticsService videoAnalyticsService;

    @Autowired
    private CategoryPoolService categoryPoolService;

    public VideoEntity saveVideo(VideoEntity videoEntity) {
        return videoRepository.save(videoEntity);
    }

    public VideoEntity getVideoById(Long videoId) {
        return videoRepository.findById(videoId.toString()).orElse(null);
    }

    // New method to process a video and its pool tiers
    public void processVideoPoolTiers(Long videoId) {
        // MAKE API REQUEST FROM AI SERVER TO GET POOL TIERS AND UPDATE
        // THE RECEIVED RESPONSE CONTAINS CATEGORY AND PERCENTAGE
        // WE NEED TO USE THESE DATA TO GET VIDEO TIERS
        // THEN WE UPDATE POOL TIER AND SAVE IT


        List<PoolTier> poolTiers = List.of();

        VideoEntity videoEntity = videoRepository.getReferenceById(videoId.toString());
        videoEntity.setPoolTiers(poolTiers);

        for (PoolTier poolTier : videoEntity.getPoolTiers()) {
            double engagementScore = videoAnalyticsService.getEngagementScore(videoEntity);
            VideoTier videoTier = categoryPoolService.getVideoTier(poolTier.getCategoryPoolEntity().getId(), engagementScore);
            log.info("Video {} Tier {} in Category {}", videoEntity.getCaption(), videoTier.toString(), poolTier.getCategoryPoolEntity().getName());

            poolTier.setVideoTier(videoTier);
        }

        videoRepository.save(videoEntity);
    }
}