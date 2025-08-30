package com.backend.tier_tok.repository;

import com.backend.tier_tok.model.entity.InteractionEventEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface InteractionEventRepository extends JpaRepository<InteractionEventEntity, Long> {
}
