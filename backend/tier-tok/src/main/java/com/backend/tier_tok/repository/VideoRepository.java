package com.backend.tier_tok.repository;

import com.backend.tier_tok.model.entity.VideoEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface VideoRepository extends JpaRepository<VideoEntity, String> {
    List<VideoEntity> findByPoolTiers_CategoryPoolEntity_Id(Long categoryPoolId);
}
