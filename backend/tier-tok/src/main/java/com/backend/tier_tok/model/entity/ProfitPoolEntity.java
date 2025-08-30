package com.backend.tier_tok.model.entity;

import com.backend.tier_tok.model.DTO.CategoryPoolDTO;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Entity
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class ProfitPoolEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    private double totalFund;

    private double totalCategoryWeight;

    @OneToMany(cascade = CascadeType.ALL)
    private List<CategoryPoolEntity> categoryPoolList;
}
