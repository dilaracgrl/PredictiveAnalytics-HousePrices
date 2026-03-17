# Improvement Reasoning (Task 04)

## Baseline diagnosis
- Baseline RMSE=150.5786, MAE=106.2309, R2=-0.6251.
- Negative R2 indicates severe underfitting for this price regression problem.

## Ranked strategies
1. Non-linear ensemble model to capture interaction and non-linear effects.
2. Target-independent feature engineering (`log_minimum_nights`, `review_intensity`, `availability_rate`, `lat_lon_interaction`).
3. Drop high-cardinality text/ID fields (`id`, `name`, `host_name`) to improve stability.

## Risks
- Gradient boosting can overfit noisy tails.
- Random forest may smooth extreme price variation.
- Engineered features may add weak/noisy signal.

## Leakage control
- One train/test split with SEED=42.
- No test-informed tuning decisions.
- No target-derived features.

## EDA context excerpt
# EDA Summary (Task 02)

## Target Variable: `price`
- `price` is strongly right-skewed (skewness = 19.12) with a long tail.
- Key quantiles: 95th=355.0, 99th=799.0, 99.5th=1000.0; max remains very high in raw ingested data.
- For Task 03 modelling, consider robust handling of the target (for example log-transform during model training pipeline) and metrics less sensitive to extreme values.

## Most Important Feature Signals
- `room_type` is a major signal with clear median-price separation.
- `neighbourhood_group` also separates price levels, and interaction with `room_type` is strong.
- Geographic coordinates (`latitude`, `longitude`) show clear spatial price structure.
- Review and availability features have weaker linear correlation but may still add non-linear predictive value.

## Relationships and Subgroups
- Manhattan + Entire home/apt forms the highest-price subgroup.
- Shared/private room listings are consistently lower-price, but spread varies by borough.
- Spatial scatter s

