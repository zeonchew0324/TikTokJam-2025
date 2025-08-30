<img src="TierTok.jpg" width="300" height="200" />

## TierTok

TierTok is a proof-of-concept platform that categorizes videos into distinct categories and tiers. Within each tier, content creators are compensated according to a custom algorithm that balances engagement metrics and content quality. This approach not only addresses the issue of creators competing solely within their own categories but also ensures that high-quality, emerging creators are fairly rewarded and supported.

## Features
1. **Value Evaluation Algorithm**: The **Final Tier Score (FTS)** algorithm serves as the primary tool for evaluating content value. Moving beyond simple engagement metrics, it introduces the Quality Multiplier (QM), a unique component designed to provide a significant boost to high-quality content that has not yet achieved widespread virality. The algorithm's sophistication lies in its combination of a logarithmic Raw Engagement Score (RES) and the exponential decay of the QM, ensuring a fair and nuanced assessment of all content.

2. **Tiered, Categorical Pool System**: This system establishes a merit-based reward structure by first organizing content into distinct categories using a **clustering algorithm**. After this categorization, the **Final Tier Score (FTS)** is used to rank videos within each cluster. Based on their FTS, videos are assigned to specific tiers (e.g., Bronze, Silver, Gold, Platinum). This approach ensures that rewards are distributed equitably, based on both content quality and genuine engagement.

3. **Fraud Detection Bot**: 

## Algorithm
In contrast to the traditional accumulation video views, the total view count of a video is calculated
based on cascade window to give more emphasis on the most recent view counts, while associating the past
view counts with decay factor $\lambda$.

$$TotalViewCount = \sum_{k=0}^n{Past \ k^{th} \ month \ views \times e^{-\lambda k}} $$
where $k=0$ represents current month view statistics.

We shall define $WatchTimeRatio$ as follow:

$$WatchTimeRatio = \frac{WatchTime}{Views \times VideoLength}$$

This gives a more insightful statistic related to $WatchTime$, as $WatchTimeRatio$ measures the 
viewer's retention on a particular video.

Another important metric, $CommentRatio$ measures
$$CommentRatio = \frac{Comments}{Likes}$$
to gauge the viewers' engagement via comments and mitigate the influence of inauthentic likes.

Every video is evaluated quantitatively with an engagement score based on a few metrics.

$$EngagementScore = \alpha \times log(TotalViewCount + 1) + \beta \times WatchTimeRatio + \gamma \times CommentRatio$$

where $\alpha, \beta, \gamma$ are dynamic coeffiecients that can be adjusted to represent holistic engagement metrics.

### Payout

The total payout is aggregated and allocated to *category pool* using weights calculated from the videos in each pool

$${pool \ fund}_{i} = \frac{w_i}{\sum{w}} \times total \ fund$$


where $w_i$ is the *weights* for each category, calculated by:

$$w_i = \sum_{k=1}^n{EngagementScore_{sorted}}$$

to achieve mass bot content prevention and mitigate the tail risk by summing top n engagement scores 

### Tier fund allocation

Each category is divided into 4 tiers, ranked by their *EngagementScore*
$$
Tier\ 1 - Top\ 5 \% \ of \ video - receives\ 32.5\%\ of\ the\ pool\ fund\newline
Tier\ 2 - Top\ 5\%-20 \% \ of \ video - receives\ 27.5\%\ of\ the\ pool\ fund\newline
Tier\ 3 - Top\ 20\%-50 \% of \ video - receives\ 22.5\%\ of\ the\ pool\ fund\newline
Tier\ 4 - Bottom\ 17.5 \% \ of \ video - receives\ 17.5\%\ of\ the\ pool\ fund\newline
$$

### Allcoate Allocate payout from tier fund to video (content creators)

Each video in the tier is allocated fund based on their individual weights $IW$
$$IW = log(EngagementScore+1) \times QM$$
where $QM$, quality multiplier is defined as
$$QM = 1 + CQS \times MaxBonus \times e^{- EngagementScore/k}$$

where $CQS$ is ContentQualityScore given by Gemini, MaxBonus is the maximum bonus multiplier , $k$ is the scaling factor. 

$$Individual Payout = \frac{IW}{\sum{IW}}\times TierFund $$
## Getting Started With Our App
1. Clone repository:
 <pre> git clone https://github.com/zeonchew0324/TikTokJam-2025.git </pre>

2. Install dependencies:
 <pre> pip install -r requirements.txt </pre>

3. Change to the frontend folder:
  <pre> cd frontend </pre>

4. Run our app!
 <pre> npm run dev </pre>

Open your browser and navigate to the URL shown in the terminal (usually http://localhost:5173) to see the result.

