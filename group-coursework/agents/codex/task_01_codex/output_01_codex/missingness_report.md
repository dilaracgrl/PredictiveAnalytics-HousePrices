# Missingness Report

| column | missing_count | missing_pct | handling_strategy | justification |
|---|---:|---:|---|---|
| id | 0 | 0.0000 | keep | No missing values. |
| name | 16 | 0.0327 | fill with 'Unknown' | Text field with very low missingness; preserve row count. |
| host_id | 0 | 0.0000 | drop | Identifier only; near-unique and not useful as a predictive feature. |
| host_name | 21 | 0.0429 | fill with 'Unknown' | Low missingness in host name text; preserve rows. |
| neighbourhood_group | 0 | 0.0000 | keep | No missing values. |
| neighbourhood | 0 | 0.0000 | keep | No missing values. |
| latitude | 0 | 0.0000 | keep | No missing values. |
| longitude | 0 | 0.0000 | keep | No missing values. |
| room_type | 0 | 0.0000 | keep | No missing values. |
| price | 0 | 0.0000 | keep | Target variable; no missing values. Do not transform at ingestion. |
| minimum_nights | 0 | 0.0000 | clip at 99th percentile | Extreme values likely represent rare/non-standard listings and can dominate models. |
| number_of_reviews | 0 | 0.0000 | keep | No missing values. |
| last_review | 10052 | 20.5583 | drop | High missingness (~20.56%), date-like field and sparse for never-reviewed listings. |
| reviews_per_month | 10052 | 20.5583 | fill missing with 0 | Missingness means no reviews yet; zero is semantically meaningful. |
| calculated_host_listings_count | 0 | 0.0000 | keep | No missing values. |
| availability_365 | 0 | 0.0000 | keep | No missing values. |

## Strategy Notes
- Decisions documented in notebook markdown cells and outlier_flags.txt.

