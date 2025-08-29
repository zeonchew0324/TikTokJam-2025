package com.backend.tier_tok.service;

import com.backend.tier_tok.model.entity.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.List;

@Service
public class VideoPayoutCalculatorService {

    public double getVideoPayout(VideoEntity videoEntity, double engagementScore) {
        double totalPayout = 0.0;

        for (PoolTier poolTier : videoEntity.getPoolTiers()) {
            CategoryPoolEntity categoryPool = poolTier.getCategoryPoolEntity();
            double categoryPercentage = poolTier.getCategoryPercentage();
            VideoTier videoTier = poolTier.getVideoTier();

            double videoWeight = Math.log(engagementScore * categoryPercentage + 1);

            double tierTotalWeight = categoryPool.getVideoTierToWeightMap().getOrDefault(videoTier, 0.0);
            double tierFund = categoryPool.getVideoTierToFundMap().getOrDefault(videoTier, 0.0);

            if (tierTotalWeight > 0) {
                totalPayout += (videoWeight / tierTotalWeight) * tierFund;
            }
        }
        return totalPayout;
    }
}
