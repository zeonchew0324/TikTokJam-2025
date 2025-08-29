package com.backend.tier_tok.service;

import com.backend.tier_tok.model.DTO.CategoryPoolDTO;
import com.backend.tier_tok.model.DTO.ProfitPoolDistributionResponseDTO;
import com.backend.tier_tok.model.entity.ProfitPoolEntity;
import com.backend.tier_tok.repository.ProfitPoolRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
@Slf4j
public class ProfitPoolService {

    @Autowired
    private ProfitPoolRepository profitPoolRepository;

    @Autowired
    private CategoryPoolService categoryPoolService;

    // Assumes there is a single ProfitPoolEntity with ID 1
    private static final Long PROFIT_POOL_ID = 1L;

    // Scheduled operation to distribute funds from big pool to category pool,
    // and update video tier fund for each category
    public ProfitPoolDistributionResponseDTO distributeFundsToCategories() {
        Optional<ProfitPoolEntity> profitPoolOpt = profitPoolRepository.findById(PROFIT_POOL_ID);
        if (profitPoolOpt.isPresent()) {
            ProfitPoolEntity profitPool = profitPoolOpt.get();
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
            profitPoolRepository.save(profitPool);

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
}
