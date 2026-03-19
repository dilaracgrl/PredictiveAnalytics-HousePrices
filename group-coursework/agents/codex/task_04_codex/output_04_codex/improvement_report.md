# Improvement Report (Task 04)

## Implemented strategies
1. GradientBoostingRegressor with engineered features.
2. RandomForestRegressor with engineered features.

## Honest comparison
- Baseline: RMSE=150.5786, MAE=106.2309, R2=-0.6251
- Improved (random_forest): RMSE=86.5290, MAE=48.4731, R2=0.4634
- Non-selected strategy: Gradient boosting: RMSE=89.0722, MAE=50.4862, R2=0.4314

## Leakage checks
- Same split protocol as baseline with SEED=42.
- No test-based feature engineering or tuning.
- No target-derived leakage features.
