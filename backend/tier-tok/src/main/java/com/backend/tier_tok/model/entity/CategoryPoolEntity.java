package com.backend.tier_tok.model.entity;

import com.backend.tier_tok.model.converter.PriorityQueueConverter;
import com.backend.tier_tok.model.converter.VideoTierMapConverter;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;
import java.util.PriorityQueue;

@Data
@Entity
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class CategoryPoolEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String name;

    @Column(nullable = false)
    private double totalCategoryPoolFund;

    @Column(nullable = false)
    private double totalCategoryPoolWeight;

    // Persist PriorityQueue by converting it to a JSON string
    @Convert(converter = PriorityQueueConverter.class)
    @Column(name = "top_engagement_score_list", columnDefinition = "TEXT")
    private PriorityQueue<Double> topEngagementScoreList;

    // Persist Map by converting it to a JSON string
    @Convert(converter = VideoTierMapConverter.class)
    @Column(name = "video_tier_to_weight_map", columnDefinition = "TEXT")
    private Map<VideoTier, Double> videoTierToWeightMap;

    // Persist Map by converting it to a JSON string
    @Convert(converter = VideoTierMapConverter.class)
    @Column(name = "video_tier_to_fund_map", columnDefinition = "TEXT")
    private Map<VideoTier, Double> videoTierToFundMap;
}
