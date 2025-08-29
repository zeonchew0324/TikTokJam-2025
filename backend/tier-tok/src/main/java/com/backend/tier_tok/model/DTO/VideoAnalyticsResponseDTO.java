package com.backend.tier_tok.model.DTO;

import com.backend.tier_tok.model.entity.UserEntity;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class VideoAnalyticsResponseDTO {
    private String videoId;

    private String caption;

    private double watchTime;

    // the total view count since video upload to last month
    private long pastMonthsTotalViewCount;

    // can get recent view count through pastMonthsTotalViewCount
    private long totalViewCount;

    private long likeCount;

    private long commentCount;

    private UserEntity creator;

    private List<PayoutDTO> payoutDTOList;
}
