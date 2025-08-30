package com.backend.tier_tok.model.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Entity
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class UserEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private long id;

    private String username;

    @Column(nullable = false, columnDefinition = "integer default 100")
    private int reputationScore;

    private LocalDateTime createdAt;

    @Column(nullable = false, columnDefinition = "boolean default false")
    private boolean hasProfilePic;

    @Column(nullable = false, columnDefinition = "bigint default 0")
    private long followerCount;

    @Column(nullable = false, columnDefinition = "bigint default 0")
    private long followingCount;

    @Column(nullable = false, columnDefinition = "integer default 0")
    private int bioLength;

    @Column(nullable = false, columnDefinition = "boolean default false")
    private boolean isVerified;

    @Column(nullable = false, columnDefinition = "boolean default false")
    private boolean isLocationConsistent;

    private String ipAddress;

    @Column(nullable = false, columnDefinition = "integer default 0")
    private int timezone;
}
