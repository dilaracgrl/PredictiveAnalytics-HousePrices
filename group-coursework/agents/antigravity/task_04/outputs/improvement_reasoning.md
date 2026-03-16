# Baseline Diagnosis and Improvement Reasoning

**Weaknesses Diagnosed:**
The Ridge regression baseline failed because it expects spatial coordinates (`latitude`, `longitude`) to be simple linear planes, and combining this with static One-Hot Encoding for borough groups limits the capacity to model hyper-localized subgroups (e.g. specific zip code neighborhoods combined with specific room types).

**Strategy 1: Upgrade to HistGradientBoostingRegressor (High Impact)**
- *Why:* Gradient boosting trees can branch inherently to create multi-dimensional geographic bounding boxes by repeatedly splitting lat/long. They also model deep feature intersections natively, negating the requirement for explicit cross-feature engineering.
- *Risk:* Tree models can easily overfit sparse leaf nodes, but `HistGradientBoostingRegressor` brings built-in mitigations like structural regularization and l2 penalties.

**Strategy 2: High-Cardinality Feature Engineering (Medium Impact)**
- *Why:* The baseline ignored the highly predictive `neighbourhood` feature (~221 unique values) to prevent multicollinear dimensionality explosions. However, we can use Scikit-Learn's `TargetEncoder` explicitly fitted within our Pipeline.
- *Risk:* Target leakage. But fitting `TargetEncoder` rigidly on `X_train` natively utilizes cross-fitted inner folds, successfully guaranteeing that `X_test` remains untainted.