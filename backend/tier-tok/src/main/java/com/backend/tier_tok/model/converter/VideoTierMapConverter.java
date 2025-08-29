package com.backend.tier_tok.model.converter;

import com.backend.tier_tok.model.entity.VideoTier;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@Converter
public class VideoTierMapConverter implements AttributeConverter<Map<VideoTier, Double>, String> {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public String convertToDatabaseColumn(Map<VideoTier, Double> map) {
        if (map == null) {
            return null;
        }
        try {
            return objectMapper.writeValueAsString(map);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Could not serialize Map to JSON", e);
        }
    }

    @Override
    public Map<VideoTier, Double> convertToEntityAttribute(String s) {
        if (s == null || s.trim().isEmpty()) {
            return new HashMap<>();
        }
        try {
            return objectMapper.readValue(s, new TypeReference<>() {});
        } catch (IOException e) {
            throw new RuntimeException("Could not deserialize JSON to Map", e);
        }
    }
}
