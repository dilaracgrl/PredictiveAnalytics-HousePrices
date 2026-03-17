# Model Selection Reasoning — Task 03

## Chosen Model
**Ridge Regression** trained on **log1p(price)** as the target.

## Why log1p(price) as the target?
- Raw `price` is strongly right-skewed (skewness > 4). Training on raw price causes the
  squared-error loss to be dominated by expensive outliers, harming generalisation.
- log1p(price) is approximately normal — a much better fit for the linear model assumption.
- Predictions are back-transformed with np.expm1() for reporting in USD.

## Why Ridge and not plain OLS?
- After one-hot encoding categorical features, mild multicollinearity is expected.
- Ridge L2 regularisation stabilises coefficients without discarding features.
- alpha=1.0 (default) — no hyperparameter tuning; this is a baseline, not the final model.

## Why not a tree-based model as the baseline?
- Trees naturally handle non-linearities and interactions — that would skip the baseline step.
- A linear model gives a clear, interpretable lower bound. Task 04 can show the uplift
  from using a more expressive model (e.g. Random Forest, Gradient Boosting).

## Known Limitations
1. Cannot model the room_type × neighbourhood interaction without an explicit feature.
2. `neighbourhood` column excluded (200+ levels) — using borough-level grouping instead.
3. Geographic signal (latitude/longitude) captured linearly — spatial non-linearities missed.
4. Assumes additive feature contributions on the log scale.

## Features Used
- Categorical (one-hot): room_type, neighbourhood_group
- Numeric (standardised): latitude, longitude, minimum_nights, number_of_reviews,
  reviews_per_month, calculated_host_listings_count, availability_365
- Excluded: neighbourhood (high cardinality — Task 04 improvement)
