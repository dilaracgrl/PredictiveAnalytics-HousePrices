# Baseline Report (Task 03)

- SEED: 42
- Input: `../task_02_codex/output_02_codex/eda_cleaned.csv`
- Split: 80/20 train/test (`random_state=42`)
- Model: LinearRegression
- Preprocessing: ColumnTransformer with train-only fit
  - Numeric: median imputation + standard scaling
  - Categorical: most-frequent imputation + one-hot encoding

## Metrics (test set)
metric_name      value
       rmse 148.369542
        mae 104.395804
         r2  -0.577746

## Leakage prevention
All preprocessing is inside a scikit-learn pipeline fit only on `X_train, y_train`.
No operations were fit on full data before splitting.
