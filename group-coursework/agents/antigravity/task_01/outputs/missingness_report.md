# Missingness Report

|                   |   missing_count |   missing_pct |
|:------------------|----------------:|--------------:|
| reviews_per_month |           10052 |         20.56 |
| last_review       |           10052 |         20.56 |
| host_name         |              21 |          0.04 |
| name              |              16 |          0.03 |


## Handling Strategy
| Column | Strategy | Justification |
|--------|----------|---------------|
| `last_review` | Fill with `"No review"` | Null means no review left, not an unknown date. Sentinel string preserves this meaning without fabricating data. |
| `reviews_per_month` | Fill with `0.0` | Structurally linked to `last_review`; zero reviews means a rate of 0. |
| `name` | Fill with `"Unknown"` | ~0.02% missing. Sentinel keeps all rows; not heavily used for modelling. |
| `host_name` | Fill with `"Unknown"` | ~0.01% missing. Sentinel keeps all rows. |