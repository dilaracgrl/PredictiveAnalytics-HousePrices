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
- Spatial scatter shows clusters of high prices in central/high-demand zones.

## Remaining Data Quality Decisions
- Additional EDA cleaning applied: rows above the 99.5th percentile of `price` were removed for analysis-ready stability (`eda_cleaned.csv`).
- This cleaning was done for EDA/model-readiness only; train/test splitting is still deferred to Task 03.
- No held-out data was created or used.

## Feature Engineering Ideas for Task 04
- Borough x room_type interaction features.
- Spatial features (distance-to-centroid or cluster labels from latitude/longitude).
- Non-linear transforms for skewed predictors.
- Potential robust scaling/winsorization for heavy-tailed numeric variables.

## Top Correlations With Price (absolute)
longitude                        -0.258762
calculated_host_listings_count    0.130687
availability_365                  0.117916
latitude                          0.062962
number_of_reviews                -0.057829
reviews_per_month                -0.055841
