package com.backend.tier_tok.model.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Entity
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class VideoEntity {

    @Id
//    @GeneratedValue(strategy = GenerationType.IDENTITY)
    // the id is the point id
    private String id;

    @ManyToOne
    @JoinColumn(name = "creatorId")
    private UserEntity creator;

    private String caption;

    private double duration;

    private double watchTime;

    private String videoUrl;

    // the total view count since video upload to last month
    private long pastMonthsTotalViewCount;

    // can get recent view count through pastMonthsTotalViewCount
    private long totalViewCount;

    private long likeCount;

    private long commentCount;

    // Top 3 category allocation for the video
    @OneToMany(mappedBy = "videoEntity", cascade = CascadeType.ALL)
    private List<PoolTier> poolTiers;

    @Column(updatable = false, nullable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}

