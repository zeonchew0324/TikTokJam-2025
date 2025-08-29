package com.backend.tier_tok.model.DTO;

import com.backend.tier_tok.model.entity.VideoTier;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PayoutDTO {
    private String categoryName;

    private double percentage;

    private double videoPayout;

    private double engagementScore;

    private VideoTier videoTier;
}
