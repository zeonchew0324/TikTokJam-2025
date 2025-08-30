-- Disable foreign key checks to allow inserting data in any order
SET session_replication_role = replica;

-- 1. Insert a single Profit Pool
INSERT INTO profit_pool_entity (id, total_fund, total_category_weight) VALUES
(1, 100000.00, 0.0);

-- 2. Insert a few users
INSERT INTO user_entity (id, username, reputation_score) VALUES
(1, 'Alpha_Creator', 100),
(2, 'Beta_Creator', 95),
(3, 'Gamma_Creator', 88);

-- 3. Insert a few category pools
-- The `top_engagement_score_list`, `video_tier_to_weight_map`, and `video_tier_to_fund_map`
-- are empty JSON objects initially and will be populated by the algorithm.
INSERT INTO category_pool_entity (id, name, total_category_pool_fund, total_category_pool_weight, top_engagement_score_list, video_tier_to_weight_map, video_tier_to_fund_map) VALUES
(1, 'comedy', 0.0, 0.0, '[]', '{}', '{}'),
(2, 'education', 0.0, 0.0, '[]', '{}', '{}'),
(3, 'gaming', 0.0, 0.0, '[]', '{}', '{}'),
(4, 'food', 0.0, 0.0, '[]', '{}', '{}');

INSERT INTO profit_pool_entity_category_pool_list (profit_pool_entity_id, category_pool_list_id)
VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4);

-- 4. Insert videos with realistic metrics
-- `past_months_total_view_count` and `total_view_count` are crucial for the engagement score calculation.
-- Note: The `created_at` timestamp is set manually for demo purposes.
INSERT INTO video_entity (id, caption, duration, watch_time, past_months_total_view_count, total_view_count, like_count, comment_count, created_at, creator_id, video_url) VALUES
('9274612216458326251', 'I did not know ferrari drops this', 180.0, 150.0, 100000, 125000, 5000, 800, '2025-06-25 10:00:00', 1, 'https://tiktok-video-embeddings.s3.ap-southeast-1.amazonaws.com/videos-embed/83bcfadf_Car1.mp4'),
('10262309388947372409', 'Bedtime ASMR', 300.0, 280.0, 50000, 60000, 3000, 500, '2025-07-01 12:30:00', 2, 'https://tiktok-video-embeddings.s3.ap-southeast-1.amazonaws.com/videos-embed/13c56281_ASMR.mp4'),
('10693639038944902041', 'Tung Tung Sahur', 600.0, 450.0, 80000, 95000, 8000, 1200, '2025-07-15 15:45:00', 3, 'https://tiktok-video-embeddings.s3.ap-southeast-1.amazonaws.com/videos-embed/3f9e2899_Game.mp4'),
('10998159870368524970', 'Fortuner', 240.0, 200.0, 200000, 250000, 15000, 2500, '2025-08-01 09:00:00', 1, 'https://tiktok-video-embeddings.s3.ap-southeast-1.amazonaws.com/videos-embed/e4650511_Car2.mp4'),
('13803198243386341370', 'Italian brainrot that nobody knows', 120.0, 110.0, 30000, 35000, 2000, 300, '2025-08-10 18:00:00', 2, 'https://tiktok-video-embeddings.s3.ap-southeast-1.amazonaws.com/videos-embed/d200fe67_BrainRot.mp4');

-- 5. Insert pool tiers for each video
-- The `video_tier` is left as NULL to be determined by the algorithm.
INSERT INTO pool_tier (id, category_percentage, video_tier, category_pool_id, video_id) VALUES
(1, 0.6, NULL, 1, '9274612216458326251'), -- Video 1 (Car)
(2, 0.2, NULL, 2, '9274612216458326251'), -- Video 1 (Cooking)
(3, 0.2, NULL, 3, '9274612216458326251'), -- Video 1 (Travel)
(4, 0.8, NULL, 2, '10262309388947372409'), -- Video 2 (Cooking)
(5, 0.1, NULL, 1, '10262309388947372409'), -- Video 2 (Gaming)
(6, 0.1, NULL, 3, '10262309388947372409'), -- Video 2 (Travel)
(7, 0.9, NULL, 3, '10693639038944902041'), -- Video 3 (Travel)
(8, 0.1, NULL, 2, '10693639038944902041'), -- Video 3 (Cooking)
(9, 0.95, NULL, 1, '10998159870368524970'), -- Video 4 (Gaming)
(10, 0.05, NULL, 3, '10998159870368524970'), -- Video 4 (Travel)
(11, 0.7, NULL, 2, '13803198243386341370'), -- Video 5 (Cooking)
(12, 0.3, NULL, 3, '13803198243386341370'); -- Video 5 (Travel)



-- Re-enable foreign key checks
SET session_replication_role = default;
