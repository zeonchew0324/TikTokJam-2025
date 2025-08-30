package com.backend.tier_tok.model.DTO;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class InteractionEventRequestDTO {
    private String user_id;

    private String video_id;

    private String event_id;

    private double engagement_duration;

    private long account_age_days;

    private long followers_count;

    private long following_count;

    private int profile_pic;

    private long bio_length;

    private int verified;

    private int location_consistent;

    private int timezone_offset;
}