# Prompt Log — Task 04: Improving Performance

## Iteration 1
**Prompt:**
```
Starting from the baseline in task_03_claude (Ridge on log1p(price),
RMSE=83.32), improve model performance.

Try at least two strategies:
Strategy A: Ridge + feature engineering (isolates the feature impact).
Strategy B: Random Forest + feature engineering (combined improvement).

Feature engineering to include (all fitted on train only to prevent leakage):
- neighbourhood_target_enc: mean log1p(price) per neighbourhood, computed on
  train set only.
- geo_cluster: k-means (k=20) on latitude/longitude, fitted on train only.
- log1p transforms on minimum_nights, number_of_reviews,
  calculated_host_listings_count.
- Interaction feature: room_type + neighbourhood_group as a combined string.
- Binary flags: has_reviews (number_of_reviews > 0), is_professional_host
  (calculated_host_listings_count > 1).

Show baseline vs improved metrics side by side in outputs_claude/improved_results.csv
with columns: model, RMSE_USD, MAE_USD, R2_log, R2_raw.
Save the best model as outputs_claude/improved_pipeline_rf.pkl.
Write outputs_claude/improvement_reasoning.md justifying the approach and
confirming no leakage was introduced.
Use SEED = 42. Relative paths only.
```
**What happened:**
The agent implemented both strategies. Strategy A (Ridge + FE): RMSE 80.09, R²=0.410. Strategy B (RF + FE): RMSE 74.87, R²=0.485. Both beat the baseline (83.32). RF was selected as best. The neighbourhood target encoder and geo-clustering were correctly fitted inside the training pipeline on `X_train` only.

However, reviewing the training code, I noticed LightGBM was also tested in an earlier draft with `eval_set=[(X_val, y_val)]` for early stopping — this gave LightGBM an information advantage over the other models. I flagged this before it was included in the final outputs (see Iteration 2).

---

## Iteration 2
**Prompt:**
```
I noticed the LightGBM candidate model uses eval_set=[(X_val, y_val)] for
early stopping. This leaks validation labels into the training procedure —
LightGBM sees the validation set to decide when to stop, giving it an unfair
advantage over Ridge and RF which never saw validation data.

Fix this: create an internal 90/10 stratified split from X_train for early
stopping only. The original X_val must remain completely untouched until
final metric comparison. Then re-run the full comparison.
```
**What happened:**
The agent rewrote the LightGBM training block to use an internal train/inner-val split (90/10 from `X_train`) for early stopping, keeping `X_val` reserved for final comparison only. After this fix, Random Forest still performed best (RMSE 74.87 vs LightGBM ~77), confirming the original ranking was correct. The corrected results were saved to `improved_results.csv`.

---

## Iteration 3
**Prompt:**
```
The feature importance plot is hard-coded to show LightGBM importances:
  'LightGBM-Tuned' if 'LightGBM-Tuned' in models else 'LightGBM'
This always selects LightGBM even though Random Forest was chosen as best.
Fix the plot to derive feature importances from the actual best model
(the one with the lowest RMSE), not a hard-coded name.
```
**What happened:**
The agent fixed the feature importance section to use `best_model_name = results_df.loc[results_df['RMSE_USD'].idxmin(), 'model']` and derive importances from that object. The plot now correctly shows Random Forest feature importances, with `room_type`, `neighbourhood_target_enc`, and `geo_cluster` as the top features. The final `improved_pipeline_rf.pkl` and `improvement_reasoning.md` were saved.
