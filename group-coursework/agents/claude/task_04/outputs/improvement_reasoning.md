# Improvement Reasoning — Task 04

## Baseline Weaknesses Diagnosed
1. Heteroscedasticity — residual variance grows with predicted price (linear model limitation).
2. Neighbourhood granularity lost — only 5 boroughs used; within-borough price variation is large.
3. No interaction terms — room_type × neighbourhood_group is the strongest signal but ignored.
4. Skewed numerics fed raw — minimum_nights and number_of_reviews are right-skewed; log transforms help linear models.

## Strategies Ranked by Expected Impact

### 1. Random Forest (High impact)
Directly addresses weaknesses 1 and 3. Trees capture non-linearities and feature interactions
without requiring explicit product terms. No assumption of additive linear effects.
Risk: slower to train; may overfit with too many trees (mitigated by using n_estimators=200,
max_features='sqrt', and min_samples_leaf=5).

### 2. Feature Engineering (High impact, orthogonal)
Addresses weaknesses 2 and 4. Key engineered features:
- neighbourhood_target_enc: mean log1p(price) per neighbourhood (train-only, prevents leakage)
- geo_cluster: k-means (k=20) on lat/lon (fitted on train only)
- log1p transforms on minimum_nights, number_of_reviews, calculated_host_listings_count
- Interaction: room_type + neighbourhood_group as a combined categorical
- Binary flags: has_reviews, is_professional_host

### 3. Hyperparameter Tuning (Medium impact)
Light CV-based tuning on train set only. Applied to Random Forest max_depth and min_samples_leaf.
Test set never used for any tuning decision.

## Implementation Plan
- Model A: Ridge + Feature Engineering (isolates feature impact)
- Model B: Random Forest + Feature Engineering (combined improvement)
- Compare both against the baseline using identical metrics and test set.
