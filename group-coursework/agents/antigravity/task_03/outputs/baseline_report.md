# Baseline Model Report

**SEED:** 42  
**Train/test split:** 80/20  
**Model:** Ridge Regression with TransformedTargetRegressor (log1p)

## Preprocessing

- **Drop Features:** Evaluated only robust modeling features. Text features (`name`, `id`) skipped entirely.
- **Numeric:** Standard scaling applied to nights, reviews, and coordinate data via `StandardScaler`.
- **Categorical:** `neighbourhood_group` and `room_type` converted to dense one-hot sets via `OneHotEncoder(handle_unknown='ignore')`.
- **Integrity Guarantee:** Standard scaler and HotEncoder fitted exclusively within Pipeline encapsulation strictly on the X_train index.
## Results
| metric_name   |   value |
|:--------------|--------:|
| RMSE          | 115.18  |
| MAE           |  56.34  |
| R-squared     |   0.236 |

## Limitations

Our baseline achieves substantial error on extreme value listings. The linear additive relationship assumed by Ridge does not accurately isolate hyper-granular interactions (e.g. coordinates and specific rooms) which an advanced model in Task 04 could split smoothly.
