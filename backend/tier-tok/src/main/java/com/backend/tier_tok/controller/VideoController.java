package com.backend.tier_tok.controller;

import com.backend.tier_tok.model.DTO.ProfitPoolDistributionResponseDTO;
import com.backend.tier_tok.model.entity.SuspiciousBotEntity;
import com.backend.tier_tok.model.entity.SuspiciousCreatorBotEntity;
import com.backend.tier_tok.model.DTO.VideoAnalyticsResponseDTO;
import com.backend.tier_tok.model.entity.InteractionEventEntity;
import com.backend.tier_tok.model.entity.InteractionType;
import com.backend.tier_tok.service.InteractionService;
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

    @Autowired
    private InteractionService interactionService;

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

//    @PostMapping("/{videoId}/process-tiers")
//    public ResponseEntity<String> processVideoTiers(@PathVariable String videoId) {
//        log.info("Processing video tiers for: {}", videoId);
//        try {
//            videoService.processVideoPoolTiers(videoId);
//            return ResponseEntity.ok("Video pool tiers processed successfully.");
//        } catch (Exception e) {
//            log.error("Error processing video tiers for ID {}: {}", videoId, e.getMessage());
//            return ResponseEntity.badRequest().body("Error processing video tiers: " + e.getMessage());
//        }
//    }

    @PostMapping("/refresh-pool-funds")
    public ResponseEntity<ProfitPoolDistributionResponseDTO> refreshPoolAndTierFund() {
        log.info("Refreshing all profit pool funds and distributing to category tiers.");
        ProfitPoolDistributionResponseDTO responseDTO = profitPoolService.distributeFundsToCategories();
        return ResponseEntity.ok(responseDTO);
    }

    @PostMapping("/interaction/{videoId}")
    public ResponseEntity<InteractionEventEntity> interactVideo(@RequestParam String interactionType, @PathVariable String videoId) {
        return ResponseEntity.ok(interactionService.interactVideo(InteractionType.valueOf(interactionType), videoId));
    }

    @PostMapping("/check-bots")
    public ResponseEntity<List<SuspiciousBotEntity>> checkForSuspiciousBot() {
        return ResponseEntity.ok(interactionService.runSuspiciousBotCheck());
    }

    @GetMapping("/bots")
    public ResponseEntity<List<SuspiciousBotEntity>> getSuspiciousBotList() {
        return ResponseEntity.ok(interactionService.getSuspiciousBotList());
    }

    @PostMapping("/bots")
    public ResponseEntity<Void> resolveSuspiciousBot(@RequestParam Long id, @RequestParam Boolean isPenalize) {
        interactionService.resolveSuspiciousBot(id, isPenalize);
        return ResponseEntity.ok(null);
    }

    @GetMapping("/creator-bots")
    public ResponseEntity<List<SuspiciousCreatorBotEntity>> getSuspiciousCreatorBotList() {
        return ResponseEntity.ok(interactionService.getSuspiciousCreatorBotList());
    }

    @PostMapping("/creator-bots")
    public ResponseEntity<Void> resolveSuspiciousCreatorBot(
            @RequestParam Long id, @RequestParam Boolean isPenalize) {
        interactionService.resolveSuspiciousCreatorBot(id, isPenalize);
        return ResponseEntity.ok(null);
    }

    @PostMapping("/receive-creator-bots")
    public ResponseEntity<Void> getCreatorBotsFlag(@RequestParam String videoId, @RequestParam Double similarityScore) {
        interactionService.handleGetCreatorBotsFlag(videoId, similarityScore);
        return ResponseEntity.ok(null);
    }
}