# EDA Summary — NYC Airbnb 2019

## Target Variable
- `price` is strongly right-skewed (skewness > 4 raw).
- log1p(price) is approximately normal — **use log1p(price) as the regression target in Task 03**.
- After EDA cleaning, price is capped at the 99th percentile; rows above this threshold are removed.

## Most Predictive Features
1. `room_type` — largest single-feature price differentiator.
2. `neighbourhood_group` (borough) — clear price hierarchy: Manhattan > Brooklyn > Queens > Staten Island > Bronx.
3. `neighbourhood` — fine-grained; high cardinality (200+ values); use target encoding or grouping.
4. `latitude` / `longitude` — spatial price gradient, especially within Manhattan.
5. `availability_365` — bimodal; reflects host commitment level.
6. `calculated_host_listings_count` — proxy for professional hosts who price more strategically.

## Redundant / Problematic Features
- `reviews_per_month` and `number_of_reviews` are correlated; consider dropping one.
- `minimum_nights` was clipped at 30 to remove long-term rental outliers.

## Data Cleaning Applied in Task 02
- Removed listings with price > 99th percentile (extreme luxury outliers).
- Clipped `minimum_nights` at 30 nights.
- Output: `eda_cleaned.csv` (this is the input for Task 03).

## Feature Engineering Recommendations for Task 04
1. Room × Borough interaction term.
2. Geo-cluster feature (k-means on latitude/longitude).
3. Binary `has_reviews` and `is_professional_host` flags.
4. Availability bucket (low/medium/high).
5. log1p transform on skewed numeric features.
