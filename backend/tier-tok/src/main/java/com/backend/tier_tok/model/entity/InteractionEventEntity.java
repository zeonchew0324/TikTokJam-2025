package com.backend.tier_tok.model.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
public class InteractionEventEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private long id;

    private String videoId;

    @ManyToOne(cascade = {CascadeType.PERSIST, CascadeType.MERGE})
    private UserEntity creator;

    @Enumerated(EnumType.STRING)
    private InteractionType interactionType;

    private LocalDateTime timestamp;

    private double engagementDuration;
}

