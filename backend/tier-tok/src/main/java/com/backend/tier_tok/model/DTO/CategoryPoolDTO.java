package com.backend.tier_tok.model.DTO;

import com.backend.tier_tok.model.entity.VideoTier;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class CategoryPoolDTO {
    private long id;

    private String name;

    private double totalCategoryPoolFund;

    private Map<VideoTier, Double> videoTierToWeightMap;

    private Map<VideoTier, Double> videoTierToFundMap;
}
