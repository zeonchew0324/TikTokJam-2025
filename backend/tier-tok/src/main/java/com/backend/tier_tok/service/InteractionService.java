package com.backend.tier_tok.service;

import com.backend.tier_tok.model.entity.SuspiciousBotEntity;
import com.backend.tier_tok.model.entity.SuspiciousCreatorBotEntity;
import com.backend.tier_tok.model.entity.InteractionEventEntity;
import com.backend.tier_tok.model.entity.InteractionType;
import com.backend.tier_tok.model.entity.UserEntity;
import com.backend.tier_tok.model.entity.VideoEntity;
import com.backend.tier_tok.repository.*;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.HttpHeaders;

import java.time.LocalDateTime;
import java.util.*;

@Service
@Slf4j
public class InteractionService {
    @Autowired
    private InteractionEventRepository interactionEventRepository;

    @Autowired
    private SuspiciousBotRepository suspiciousBotRepository;

    @Autowired
    private SuspiciousCreatorBotRepository suspiciousCreatorBotRepository;

    @Autowired
    private VideoRepository videoRepository;

    @Autowired
    private UserRepository userRepository;

    private static final int SAMPLING_USER = 200;

    @Value("${ai.server.base.url}")
    private String base_url;

    @Transactional
    public InteractionEventEntity interactVideo(InteractionType interactionType, String videoId) {
        VideoEntity videoEntity = videoRepository.findById(videoId).orElseThrow();
        return interactionEventRepository.save(
                InteractionEventEntity.builder()
                        .videoId(videoId)
                        .creator(videoEntity.getCreator())
                        .interactionType(interactionType)
                        .timestamp(LocalDateTime.now())
                        .engagementDuration(120.0)
                        .build()
        );
    }

    @Transactional
    public List<SuspiciousBotEntity> runSuspiciousBotCheck() {
        // Sample up to 200 random users
        List<UserEntity> sampledUsers = sampleRandomUsers();

        // Get all interactions for these users
        List<InteractionEventEntity> userInteractions = getInteractionsForUsers(sampledUsers);

        // Prepare request data
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("users", sampledUsers.stream().map(UserEntity::getId).toList());
        requestBody.put("interactions", userInteractions);

        // Set up HTTP request
        String apiUrl = base_url + "/admin/run-bot-user-check";
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestBody, headers);

        // Make HTTP request
        RestTemplate restTemplate = new RestTemplate();
        List<SuspiciousBotEntity> suspiciousBots = new ArrayList<>();

        try {
            ResponseEntity<String> response = restTemplate.postForEntity(
                    apiUrl, requestEntity, String.class);

            String serverResponse = response.getBody();
            log.info("Received response from bot detection service: {}", serverResponse);

            // Process response
            ObjectMapper objectMapper = new ObjectMapper();
            JsonNode userNodes = objectMapper.readTree(serverResponse);

            if (userNodes.isArray()) {
                for (JsonNode userNode : userNodes) {
                    String userId = userNode.get("user_id").asText();
                    long numericUserId;
                    try {
                        numericUserId = Long.parseLong(userId.replaceAll("[^0-9]", ""));
                    } catch (NumberFormatException e) {
                        numericUserId = 0;
                    }

                    SuspiciousBotEntity dto = SuspiciousBotEntity.builder()
                            .userId(numericUserId)
                            .botProbability(userNode.get("bot_probability").asDouble())
                            .metadata(objectMapper.convertValue(userNode.get("metadata"), Map.class))
                            .build();

                    suspiciousBots.add(dto);
                }
            }
        } catch (Exception e) {
            log.error("Error calling bot detection service", e);
        }

        if (!suspiciousBots.isEmpty()) {
            suspiciousBotRepository.saveAll(suspiciousBots);
        }
        return suspiciousBots;
    }

    private List<UserEntity> sampleRandomUsers() {
        // Get all users
        List<UserEntity> allUsers = userRepository.findAll();

        // If we have fewer than maxCount users, return all of them
        if (allUsers.size() <= InteractionService.SAMPLING_USER) {
            return allUsers;
        }

        // Otherwise, shuffle the list and take the first maxCount elements
        Collections.shuffle(allUsers);
        return allUsers.subList(0, InteractionService.SAMPLING_USER);
    }

    private List<InteractionEventEntity> getInteractionsForUsers(List<UserEntity> users) {
        return users.stream()
                .map(UserEntity::getId)
                .map(id -> interactionEventRepository.findById(id).orElse(null))
                .filter(Objects::nonNull)
                .toList();
    }

    // remove interaction data that are after 7 days
    @Scheduled(cron = "0 0 0 * * *")
    @Transactional
    public void removeOutdatedInteractionData() {
        interactionEventRepository.findAll()
                .removeIf(interactionEvent -> interactionEvent.getTimestamp()
                        .isBefore(LocalDateTime.now().minusDays(7)));
    }

    public List<SuspiciousBotEntity> getSuspiciousBotList() {
        return suspiciousBotRepository.findAll();
    }

    @Transactional
    public void resolveSuspiciousBot(long id, boolean isPenalize) {
        SuspiciousBotEntity suspiciousBot = suspiciousBotRepository.findById(id).orElseThrow();
        UserEntity userEntity = userRepository.findById(suspiciousBot.getUserId()).orElseThrow();

        if (isPenalize) {
            userEntity.setReputationScore(userEntity.getReputationScore() - 5);
            userRepository.save(userEntity);
        }

        suspiciousBotRepository.deleteById(id);
    }

    public List<SuspiciousCreatorBotEntity> getSuspiciousCreatorBotList() {
        return suspiciousCreatorBotRepository.findAll();
    }

    @Transactional
    public void resolveSuspiciousCreatorBot(long id, boolean isPenalize) {
        SuspiciousCreatorBotEntity suspiciousCreatorBot = suspiciousCreatorBotRepository.findById(id).orElseThrow();
        UserEntity userEntity = videoRepository.findById(suspiciousCreatorBot.getVideoId()).orElseThrow().getCreator();

        if (isPenalize) {
            userEntity.setReputationScore(userEntity.getReputationScore() - 5);
            userRepository.save(userEntity);
            videoRepository.deleteById(suspiciousCreatorBot.getVideoId());
        } else {
            // TODO: MAKE API REQUEST TO AI SERVER TO GET EMBEDDING OF VIDEO
            // SHOULD JUST RETURN 200 OK STATUS CODE
            log.info("False Alarm Resolved");
        }

        suspiciousCreatorBotRepository.deleteById(id);
    }

    @Transactional
    public void handleGetCreatorBotsFlag(String videoId, double similarityScore) {
        SuspiciousCreatorBotEntity suspiciousCreatorBot = SuspiciousCreatorBotEntity.builder()
                .videoId(videoId)
                .similarityScore(similarityScore)
                .build();

        suspiciousCreatorBotRepository.save(suspiciousCreatorBot);
    }
}
