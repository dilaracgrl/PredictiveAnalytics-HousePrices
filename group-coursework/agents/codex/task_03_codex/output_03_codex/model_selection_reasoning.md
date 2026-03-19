# Model Selection Reasoning (Task 03 Baseline)

## Why this baseline model
I selected **Linear Regression** as the baseline because it is simple, fast, and highly interpretable.
This is appropriate for Task 03 where the objective is to establish a reproducible performance floor that Task 04 can improve.

## Why this preprocessing
The dataset mixes numeric and categorical features, so the baseline uses:
- median imputation + standard scaling for numeric columns,
- most-frequent imputation + one-hot encoding for categorical columns.

These steps are included in a single pipeline so preprocessing is fit on training data only.

## Split strategy
An 80/20 train/test split with `random_state=42` was used for reproducibility.
A random split is acceptable here because there is no time-order feature that requires temporal validation.

## Metric choice
Because `price` is right-skewed, RMSE can be sensitive to large errors in the tail.
MAE is included for robustness, and R2 provides relative explanatory power.
Together RMSE + MAE + R2 give a balanced baseline view.

## Known limitations of this baseline
- Linear relationships may underfit non-linear location-price dynamics.
- One-hot encoded location signals can be high-dimensional and still miss spatial continuity.
- Heavy tail behavior in `price` can dominate errors, especially under RMSE.

## EDA context used
The EDA summary indicated strong room-type and location effects, right-skewed price, and interaction patterns.
This baseline intentionally does not model interactions explicitly; those are reserved for Task 04 improvements.

---
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
reviews_per_month                -0.055841

