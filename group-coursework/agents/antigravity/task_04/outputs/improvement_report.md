# Improvement Report

**SEED:** 42  
**Improved model:** HistGradientBoostingRegressor (logged via TransformedTargetRegressor)

## What I tried
1. **Changed Estimator Class:** Upgraded from linear Ridge framework to full gradient-boosted spatial partitions (`HistGradientBoostingRegressor`).
2. **Feature Engineering - TargetEncoder:** Brought the dropped granular `neighbourhood` strings back into the modeling phase via inner-fold `TargetEncoder`. This provided the tree deep mathematical insight into granular zip codes without collapsing available memory.
## Results
| metric_name   |   baseline_value |   improved_value |   delta_pct |
|:--------------|-----------------:|-----------------:|------------:|
| RMSE          |          115.18  |         106.07   |       -7.91 |
| MAE           |           56.34  |          50.59   |      -10.21 |
| R-squared     |            0.236 |           0.3521 |       11.61 |
## Leakage Check
- All advanced steps natively bundled directly into the `ColumnTransformer` encapsulating the estimator.
- Scikit-Learn's `TargetEncoder` explicitly mandates cross-validation smoothing inside `fit()`, successfully preventing test labels (`y_test`) from implicitly informing the `X_train` transformation rules.
## Why it worked
Gradient Boosted trees intuitively isolated discrete pockets of highly expensive blocks inside the same borough grouping (identifying Manhattan-level sub-blocks). Combining this with Target-encoded features allowed the spatial tree to identify localized value multipliers against base lat/long metrics. The MAE drop definitively validated this strategy.
