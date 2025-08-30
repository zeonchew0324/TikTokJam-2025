package com.backend.tier_tok.service;

import com.backend.tier_tok.model.entity.*;
import com.backend.tier_tok.repository.CategoryPoolRepository;
import com.backend.tier_tok.repository.VideoRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Lazy;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.List;

@Service
@Slf4j
public class VideoService {
    @Autowired
    private VideoRepository videoRepository;

    @Autowired
    private CategoryPoolRepository categoryPoolRepository;

    @Autowired
    @Lazy
    private CategoryPoolService categoryPoolService;

    @Value("${ai.server.base.url}")
    private String base_url;

    public VideoEntity saveVideo(VideoEntity videoEntity) {
        return videoRepository.save(videoEntity);
    }

    public VideoEntity getVideoById(String videoId) {
        return videoRepository.findById(videoId).orElseThrow();
    }

    // New method to process a video and its pool tiers
    @Transactional
    public void processVideoPoolTiers(String videoId, double engagementScore) {
        log.info("Processing video pool tier for videoId: {}", videoId);
        VideoEntity videoEntity = videoRepository.findById(videoId).orElseThrow();

        HttpClient client = HttpClient.newHttpClient();
        String apiUrl = base_url + "/admin/categorize-video?video_id=" + videoEntity.getVideo_id();

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
                JsonNode userNodes = objectMapper.readTree(response.body());

                List<PoolTier> poolTiers = new ArrayList<>();

                if (userNodes.isArray()) {
                    for (JsonNode userNode : userNodes) {
                        String category = userNode.get("category").asText();
                        double similarityScore = userNode.get("percentage").asDouble();

                        log.info("Extracted category: {}, similarity score: {}", category, similarityScore);

                        long numericCategoryPoolId;

                        numericCategoryPoolId = switch (category) {
                            case "Family & Kids" -> 1;
                            case "Documentary" -> 2;
                            case "Gaming" -> 3;
                            case "Food & Drink" -> 4;
                            default -> 0;
                        };

                        CategoryPoolEntity categoryPoolEntity = categoryPoolRepository.findById(numericCategoryPoolId).orElseThrow();
                        poolTiers.add(PoolTier.builder()
                                .categoryPoolEntity(categoryPoolEntity)
                                .categoryPercentage(similarityScore)
                                .videoTier(null
//                                        categoryPoolService.getVideoTier(
//                                        numericCategoryPoolId,
//                                        engagementScore * similarityScore)
                                )   // need to distribute the scores
                                .videoEntity(videoEntity)
                                .build());
                    }
                }

                videoEntity.setPoolTiers(poolTiers);
                videoRepository.save(videoEntity);

                log.info("Successfully updated video pool tier for video: {}", videoEntity.getVideo_id());

            } else {
                log.error("Error response from AI server: {}", response.statusCode());
            }

        } catch (Exception e) {
            log.error("Error calling AI Server", e);
        }
    }
}