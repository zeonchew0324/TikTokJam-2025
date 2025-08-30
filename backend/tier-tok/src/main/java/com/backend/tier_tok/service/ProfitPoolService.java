package com.backend.tier_tok.service;

import com.backend.tier_tok.model.DTO.CategoryPoolDTO;
import com.backend.tier_tok.model.DTO.ProfitPoolDistributionResponseDTO;
import com.backend.tier_tok.model.entity.ProfitPoolEntity;
import com.backend.tier_tok.repository.CategoryPoolRepository;
import com.backend.tier_tok.repository.ProfitPoolRepository;
import com.backend.tier_tok.repository.VideoRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;

@Service
@Slf4j
public class ProfitPoolService {

    @Autowired
    private ProfitPoolRepository profitPoolRepository;

    @Autowired
    private CategoryPoolService categoryPoolService;

    @Autowired
    private VideoService videoService;

    @Autowired
    private VideoAnalyticsService videoAnalyticsService;

    @Autowired
    private VideoRepository videoRepository;

    @Autowired
    private CategoryPoolRepository categoryPoolRepository;

    // Assumes there is a single ProfitPoolEntity with ID 1
    private static final Long PROFIT_POOL_ID = 1L;

    // Scheduled operation to distribute funds from big pool to category pool,
    // and update video tier fund for each category
    @Transactional
    public ProfitPoolDistributionResponseDTO distributeFundsToCategories() {
        Optional<ProfitPoolEntity> profitPoolOpt = profitPoolRepository.findById(PROFIT_POOL_ID);
        if (profitPoolOpt.isPresent()) {
            ProfitPoolEntity profitPool = profitPoolOpt.get();

            // get pool tier first for all videos first (that have no pool tiers)
            processAllVideoPoolTier();
//            videoRepository.findAll()
//                    .stream()
//                    .filter(video -> video.getPoolTiers().isEmpty())
//                    .parallel()
//                    .forEach(video -> {
//                        log.info("Processing Video Tier for {}", video.getVideo_id());
//                        videoService.processVideoPoolTiers(
//                                video.getVideo_id(),
//                                videoAnalyticsService.getEngagementScore(video)
//                        );
//                    });

//            categoryPoolRepository.findAll().forEach(
//                    categoryPoolEntity -> categoryPoolService
//                            .updateVideoTiersForCategoryPool(categoryPoolEntity.getId()));
            processAllVideoTierForAllCategories();

            double totalCategoryWeight = profitPool.getCategoryPoolList()
                    .stream()
                    .mapToDouble(category -> {
                        categoryPoolService.updateCategoryPoolTotalWeight(category.getId());
                        log.info("Category {} Weight: {}", category.getName(), category.getTotalCategoryPoolWeight());
                        return category.getTotalCategoryPoolWeight();
                    })
                    .sum();

            log.info("Total Category Weight for big pool: {}", totalCategoryWeight);

            profitPool.setTotalCategoryWeight(totalCategoryWeight);
            saveProfitPool(profitPool);

            profitPool.getCategoryPoolList().forEach(category -> {
                double categoryFund = (category.getTotalCategoryPoolWeight() / totalCategoryWeight) * profitPool.getTotalFund();
                log.info("Category {} Fund: {}", category.getName(), categoryFund);
                categoryPoolService.updateVideoTierToWeightAndFundMap(category.getId(), categoryFund);
            });

            return ProfitPoolDistributionResponseDTO.builder()
                    .id(profitPool.getId())
                    .totalFund(profitPool.getTotalFund())
                    .totalCategoryWeight(profitPool.getTotalCategoryWeight())
                    .categoryPoolList(
                            profitPool.getCategoryPoolList().stream()
                                    .map(category -> CategoryPoolDTO.builder()
                                            .id(category.getId())
                                            .name(category.getName())
                                            .totalCategoryPoolFund(category.getTotalCategoryPoolFund())
                                            .videoTierToWeightMap(category.getVideoTierToWeightMap())
                                            .videoTierToFundMap(category.getVideoTierToFundMap())
                                            .build()).toList()
                    ).build();
        }

        throw new RuntimeException("Error distribute funds to categories and tiers");
    }

    private void saveProfitPool(ProfitPoolEntity profitPool) {
        profitPoolRepository.save(profitPool);
    }

    // Process the video pool tier (without video tier first)
    private void processAllVideoPoolTier() {
        // get pool tier first for all videos first (that have no pool tiers)
        AtomicInteger count = new AtomicInteger();
        videoRepository.findAll()
                .stream()
                .filter(video -> video.getPoolTiers().isEmpty())
                .forEach(video -> {
                    log.info("{}, Processing Pool Tier for {}", count, video.getVideo_id());
                    videoService.processVideoPoolTiers(
                            video.getVideo_id(),
                            videoAnalyticsService.getEngagementScore(video)
                    );
                    count.getAndIncrement();
                });
    }

    private void processAllVideoTierForAllCategories() {
        AtomicInteger count = new AtomicInteger();
        categoryPoolRepository.findAll()
                .forEach(categoryPoolEntity -> {
                    log.info("Processing video tier for category {}", categoryPoolEntity.getName());
                    categoryPoolService
                            .updateVideoTiersForCategoryPool(categoryPoolEntity.getId());
                    count.getAndIncrement();
                });
    }
}
