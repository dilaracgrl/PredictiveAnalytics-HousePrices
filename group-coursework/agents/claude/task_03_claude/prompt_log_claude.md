# Prompt Log — Task 03: Baseline Model

## Iteration 1
**Prompt:**
```
Build a baseline regression model using outputs_claude/eda_cleaned.csv from
task_02_claude as input. Split 80/20 with SEED=42.

Fit all preprocessing (scaling, encoding) on the train set only — never on
the full dataset before splitting.

Use a simple linear model as the baseline. Because price is right-skewed,
train on log1p(price) and back-transform predictions with expm1() for reporting.

Report RMSE, MAE, and R² on the test set in USD (i.e. after back-transforming).
Save results to outputs_claude/baseline_results.csv.
Save the trained model/pipeline as outputs_claude/baseline_pipeline.pkl.
Write a model_selection_reasoning.md explaining the model choice, split
details, seed, preprocessing steps, and known limitations.
Use SEED = 42 throughout. Relative paths only.
```
**What happened:**
The agent chose Ridge Regression with log1p(price) as the target, one-hot encoding for `room_type` and `neighbourhood_group`, and standardised numerics. All preprocessing was inside a scikit-learn Pipeline fitted on `X_train` only. The model was saved as `baseline_pipeline.pkl` and results to `baseline_results.csv` (columns: split, RMSE_USD, MAE_USD, R2_log, R2_raw). Test RMSE = 83.32 USD, R² = 0.549 on log scale. `model_selection_reasoning.md` documented the rationale, limitations, and features used. The `neighbourhood` column (200+ levels) was excluded with explicit justification — left for Task 04.

Note: output files use different names from the spec (`baseline_pipeline.pkl` instead of `model.pkl`, `model_selection_reasoning.md` instead of `baseline_report.md`). This caused one automated check to fail — score recorded as 4/5.

---

## Iteration 2
**Prompt:**
```
The baseline_results.csv currently only reports test-set metrics. Please also
add a train-set row so we can check for overfitting. Keep the same columns:
split, RMSE_USD, MAE_USD, R2_log, R2_raw.
```
**What happened:**
The agent added a Train row to `baseline_results.csv`. Train RMSE = 83.65, Test RMSE = 83.32 — essentially identical, confirming no overfitting for the linear model. This also made the results table more informative for the Task 04 comparison.
