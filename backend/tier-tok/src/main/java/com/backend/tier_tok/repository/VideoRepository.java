package com.backend.tier_tok.repository;

import com.backend.tier_tok.model.entity.VideoEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface VideoRepository extends JpaRepository<VideoEntity, String> {
//    List<VideoEntity> findByPoolTiers_CategoryPoolEntity_Id(Long categoryPoolId);

    // Query to find videos by category ID without using pool tiers
    @Query(value = "SELECT v FROM VideoEntity v JOIN v.poolTiers pt WHERE pt.categoryPoolEntity.id = :categoryId")
    List<VideoEntity> findVideosByCategoryId(@Param("categoryId") Long categoryId);
}
