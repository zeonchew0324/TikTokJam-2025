package com.backend.tier_tok.repository;

import com.backend.tier_tok.model.entity.SuspiciousBotEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SuspiciousBotRepository extends JpaRepository<SuspiciousBotEntity, Long> {
}
