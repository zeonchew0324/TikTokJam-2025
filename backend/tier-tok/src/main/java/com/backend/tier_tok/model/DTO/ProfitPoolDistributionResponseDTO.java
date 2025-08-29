package com.backend.tier_tok.model.DTO;

import com.backend.tier_tok.model.entity.CategoryPoolEntity;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class ProfitPoolDistributionResponseDTO {
    private int id;

    private double totalFund;

    private double totalCategoryWeight;

    private List<CategoryPoolDTO> categoryPoolList;
}
