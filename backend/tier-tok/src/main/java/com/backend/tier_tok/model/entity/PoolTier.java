package com.backend.tier_tok.model.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
public class PoolTier {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_pool_id", nullable = false)
    private CategoryPoolEntity categoryPoolEntity;

    @Column(nullable = false)
    private double categoryPercentage;

    @Enumerated(EnumType.STRING)
    private VideoTier videoTier;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "video_id", nullable = false)
    private VideoEntity videoEntity;
}
