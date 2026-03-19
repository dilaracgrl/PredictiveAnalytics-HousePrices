# Prompt Log — Task 04: Improving Performance

## Iteration 1
**Prompt:**
```
You are helping with a data science coursework project.
The dataset is the New York City Airbnb Open Data (2019).

Your inputs:
  Dataset:          ../task_02/outputs/eda_cleaned.csv
  Baseline results: ../task_03/outputs/baseline_results.csv
  Baseline model:   ../task_03/outputs/baseline_model.pkl
  EDA findings:     ../task_02/outputs/eda_summary.md

Project goal: predict Airbnb nightly listing price (regression on `price`).

Your job is Task 04: Improving Performance.
Work entirely inside this notebook. Save all outputs to outputs/.

SEED = 42

--- WHAT YOU NEED TO DELIVER ---

1. Diagnose the baseline before attempting to improve it
   Load and display the baseline results.
   What are its weaknesses? Where does it fail?
   Look at the residuals and predictions from Task 03 — what patterns do you see?
   Write a clear diagnosis in markdown before touching any code.

2. Reason about your improvement strategy BEFORE implementing anything
   Based on your EDA summary and baseline diagnosis, what is most likely to help?
   This dataset has features the baseline may not have used well —
   categorical variables, geographic information, review patterns.
   What strategies are available to you?
   Rank them by expected impact and justify your ranking.
   What are the risks of each approach?
   Save this reasoning to outputs/improvement_reasoning.md
   This is the most important output for the group report —
   different agents will reason differently about the same problem.

3. Implement at least two improvement strategies
   Apply the strategies you reasoned your way to.
   You are free to choose any combination of:
     - Feature engineering
     - Categorical encoding
     - Handling geographic information
     - Hyperparameter tuning
     - A different model entirely
   There is no prescribed answer — your choices should follow from your reasoning.

4. Evaluate and compare honestly
   Use the same metrics as Task 03 so results are directly comparable.
   Show the baseline result alongside your improved result.
   If something did not help, say so and analyse why.
   Honest failure analysis is more valuable for the coursework than
   a result that looks good but is not explained.
   Save a comparison to outputs/improved_results.csv and produce a comparison chart.

--- CONSTRAINTS (non-negotiable) ---

- The test set must not influence any training, tuning, or feature decisions
- Any feature derived from the target variable must be computed on train data only
- You MUST show the baseline result alongside your improved result
- Do NOT use any data source other than eda_cleaned.csv
- Document every decision in a markdown cell
- Save all outputs to outputs/ using relative paths only
```
**What happened:**
The agent diagnosed four baseline weaknesses in markdown (heteroscedasticity, lost neighbourhood granularity, no interaction terms, skewed numerics). It then ranked improvement strategies by expected impact and implemented two: Strategy A (Ridge + feature engineering) and Strategy B (Random Forest + feature engineering). Feature engineering included neighbourhood target encoding, geo-clustering (k-means k=20), log1p transforms on skewed numerics, room_type × borough interaction, and binary flags — all fitted on `X_train` only. Strategy A: RMSE 80.09. Strategy B (RF): RMSE 74.87, R²=0.485. RF selected as best model.

However, reviewing the code I noticed LightGBM was also tested with `eval_set=[(X_val, y_val)]` for early stopping — this leaked validation labels into LightGBM's training procedure, giving it an unfair advantage over Ridge and RF. Flagged and fixed before finalising outputs (see Iteration 2).

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
