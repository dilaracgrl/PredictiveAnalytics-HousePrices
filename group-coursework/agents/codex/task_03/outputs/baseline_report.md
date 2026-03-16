# Baseline Report (Task 03)

- SEED: 42
- Input: `..\task_02\outputs\eda_cleaned.csv`
- Split: 80/20 train/test (`random_state=42`)
- Model: LinearRegression
- Preprocessing: ColumnTransformer with train-only fit
  - Numeric: median imputation + standard scaling
  - Categorical: most-frequent imputation + one-hot encoding

## Metrics (test set)
metric_name      value
       rmse 150.578605
        mae 106.230877
         r2  -0.625078

## Leakage prevention
All preprocessing is inside a scikit-learn pipeline fit only on `X_train, y_train`.
No operations were fit on full data before splitting.
