# Improvement Reasoning (Task 04)

## Baseline diagnosis
- Baseline RMSE=150.5786, MAE=106.2309, R2=-0.6251.
- Negative R2 indicates severe underfitting for this regression problem.

## Ranked strategies
1. Non-linear ensemble model (Gradient Boosting / Random Forest).
2. Target-independent feature engineering.
3. Remove high-cardinality text/ID fields.

## Leakage control
- One train/test split with SEED=42.
- No test-informed tuning decisions.
- No target-derived features.

## EDA context excerpt
# EDA Summary (Task 02)

## Target Variable: `price`
- `price` is strongly right-skewed (skewness = 19.12) with a long tail.
- Key quantiles: 95th=355.0, 99th=799.0, 99.5th=1000.0.
- For Task 03, consider robust handling of the target (for example log-transform during training pipeline) and robust metrics.

## Most Important Feature Signals
- `room_type` and `neighbourhood_group` are strong price separators.
- Coordinates (`latitude`, `longitude`) show clear spatial structure.
- Interaction effects (borough x room type) appear important.

## Feature Engineering Ideas for Task 04
- Borough x room_type interactions
- Spatial features from latitude/longitude
- Robust treatment of heavy-tailed numeric variables

## Top Correlations With Price (absolute)
longitude                        -0.258762
calculated_host_listings_count    0.130687
availability_365                  0.117916
latitude                          0.062962
number_of_reviews                -0.057829
reviews_per_month        
