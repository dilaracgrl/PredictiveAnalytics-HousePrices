# EDA Summary

## Key Findings
- The target variable (`price`) is severely right-skewed and ranges identically zero up to $10,000. It requires a log-transformation for stable regression.
- Continuous numeric features (like `minimum_nights` or `availability_365`) have remarkably weak linear correlations with price.
- Location (`neighbourhood_group`) and `room_type` are the dominant structural drivers of the listing price.
- The dataset contained explicit invalid listings (prices of $0), which were dropped.

## Features of Interest
- **Promising:** `room_type` and geography (`neighbourhood_group`, `neighbourhood`, `latitude`, `longitude`).
- **Redundant/Problematic:** IDs (`id`, `host_id`) should be dropped before modeling. `reviews_per_month` and `number_of_reviews` are collinear; one might be redundant.

## Potential Issues & Preprocessing Recommendations for Task 03/04
- **Target Transform:** Crucial to use `log1p(price)` as the target variable during training, then exponentiate predictions.
- **Outliers:** `price` was capped at $1000 and `minimum_nights` capped at 365 to limit noise.
- **Feature Engineering:** Since numeric features are weak predictors, future tasks should explore Target Encoding for the high-cardinality `neighbourhood` feature, or spatial clustering using the `latitude` and `longitude` coordinates.
