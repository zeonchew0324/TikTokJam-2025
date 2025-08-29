package com.backend.tier_tok.model.converter;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

import java.io.IOException;
import java.util.PriorityQueue;

@Converter
public class PriorityQueueConverter implements AttributeConverter<PriorityQueue<Double>, String> {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public String convertToDatabaseColumn(PriorityQueue<Double> priorityQueue) {
        if (priorityQueue == null) {
            return null;
        }
        try {
            return objectMapper.writeValueAsString(priorityQueue);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Could not serialize PriorityQueue to JSON", e);
        }
    }

    @Override
    public PriorityQueue<Double> convertToEntityAttribute(String s) {
        if (s == null || s.trim().isEmpty()) {
            return new PriorityQueue<>();
        }
        try {
            return objectMapper.readValue(s, new TypeReference<>() {});
        } catch (IOException e) {
            throw new RuntimeException("Could not deserialize JSON to PriorityQueue", e);
        }
    }
}