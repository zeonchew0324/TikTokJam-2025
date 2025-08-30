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

    // the id is the point id
    @Id
    private String video_id;

    @ManyToOne(cascade = {CascadeType.PERSIST, CascadeType.MERGE})
    @JoinColumn(name = "creatorId")
    private UserEntity creator;

    @Column(columnDefinition = "TEXT")
    private String caption;

    private double duration;

    private double watchTime;

    @Column(length = 1000)
    private String videoUrl;

    // the total view count since video upload to last month
    @Column(nullable = false, columnDefinition = "bigint default 0")
    private long pastMonthsViewCount;

    // can get recent view count through pastMonthsTotalViewCount
    @Column(nullable = false, columnDefinition = "bigint default 0")
    private long totalViewCount;

    @Column(nullable = false, columnDefinition = "bigint default 0")
    private long likeCount;

    @Column(nullable = false, columnDefinition = "bigint default 0")
    private long commentCount;

    @Column(nullable = false, columnDefinition = "float default 0.0")
    private double engagementScore;

    @Column(updatable = false, nullable = false)
    private LocalDateTime createdAt;

    // Top 3 category allocation for the video
    @OneToMany(mappedBy = "videoEntity", cascade = CascadeType.ALL)
    private List<PoolTier> poolTiers;

//    @PrePersist
//    protected void onCreate() {
//        createdAt = LocalDateTime.now();
//    }
}

