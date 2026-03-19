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
