package com.backend.tier_tok.controller;

import com.backend.tier_tok.model.DTO.ProfitPoolDistributionResponseDTO;
import com.backend.tier_tok.model.DTO.VideoAnalyticsResponseDTO;
import com.backend.tier_tok.model.entity.PoolTier;
import com.backend.tier_tok.service.ProfitPoolService;
import com.backend.tier_tok.service.VideoAnalyticsService;
import com.backend.tier_tok.service.VideoService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/video")
@Slf4j
public class VideoController {

    @Autowired
    private VideoService videoService;

    @Autowired
    private VideoAnalyticsService videoAnalyticsService;

    @Autowired
    private ProfitPoolService profitPoolService;

    @GetMapping("/{videoId}/analytics")
    public ResponseEntity<VideoAnalyticsResponseDTO> getVideoAnalytics(@PathVariable String videoId) {
        log.info("Getting video analytics for: {}", videoId);
        try {
            VideoAnalyticsResponseDTO videoAnalyticsResponseDTO = videoAnalyticsService.getVideoAnalytics(videoId);
            return ResponseEntity.ok().body(videoAnalyticsResponseDTO);
        } catch (Exception e) {
            log.error("Error retrieving video analytics for ID {}: {}", videoId, e.getMessage());
            return ResponseEntity.badRequest().body(null);
        }
    }

    @PostMapping("/{videoId}/process-tiers")
    public ResponseEntity<String> processVideoTiers(@PathVariable Long videoId) {
        log.info("Processing video tiers for: {}", videoId);
        try {
            videoService.processVideoPoolTiers(videoId);
            return ResponseEntity.ok("Video pool tiers processed successfully.");
        } catch (Exception e) {
            log.error("Error processing video tiers for ID {}: {}", videoId, e.getMessage());
            return ResponseEntity.badRequest().body("Error processing video tiers: " + e.getMessage());
        }
    }

    @PostMapping("/refresh-pool-funds")
    public ResponseEntity<ProfitPoolDistributionResponseDTO> refreshPoolAndTierFund() {
        log.info("Refreshing all profit pool funds and distributing to category tiers.");
        ProfitPoolDistributionResponseDTO responseDTO = profitPoolService.distributeFundsToCategories();
        return ResponseEntity.ok(responseDTO);
    }
}