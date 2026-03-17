# Prompt Log: Task 04 - Improving Performance

> Paste each prompt you sent to the agent here, in order. Note what changed between iterations.

## Prompt Received
**Prompt:**
```
Prompt 4:
You are helping with a data science coursework project.
The dataset is the New York City Airbnb Open Data (2019).

Your inputs:
  Dataset:          ../task_02/outputs/eda_cleaned.csv
  Baseline results: ../task_03/outputs/baseline_results.csv
  Baseline model:   ../task_03/outputs/baseline_model.pkl
  EDA findings:     ../task_02/outputs/eda_summary.md

Project goal: predict Airbnb nightly listing price (regression on `price`).

Your job is Task 04: Improving Performance.

1. Diagnose the baseline before attempting to improve it
2. Reason about your improvement strategy BEFORE implementing anything
3. Implement at least two improvement strategies
4. Evaluate and compare honestly
```

## Decisions and Implementation Details
Task 04 involved surpassing the Ridge baseline by specifically targeting its categorical weakness and lack of spatial awareness. 

1. **Baseline Weakness Diagnosis**:
   - The primary weakness diagnosed was that spatial properties (like longitude/latitude pairs) represent geometric mapping constraints, yet the Ridge model treats them as boundless linear equations. It completely bypassed the ultra-granular variable `neighbourhood` (~220 zip codes) entirely out of dimensional memory constraints.

2. **Improvement Strategy 1: Tree Ensembling (`HistGradientBoostingRegressor`)**:
   - **Decision:** Shifted the architectural backbone to non-linear Gradient Boosting structurally. 
   - Gradient boosted spatial trees naturally carve boundaries continuously splitting `latitude` by `longitude` over and over, effectively building micro-location geographic square bounding boxes natively inside the leaves.
   - This framework handles Ordinal integers transparently without constructing massive memory-hogging feature matrices.
   
3. **Improvement Strategy 2: High-Cardinality Feature Engineering (`TargetEncoder`)**:
   - **Decision:** We reclaimed the incredibly predictive `neighbourhood` string by executing Target Encoding techniques natively bundled inside our `ColumnTransformer`. 
   - **Safeguarding against Leakage:** Target Encoding maps string integers to their statistical group means target value. Scikit-Learn natively performs *inner K-fold cross-validation fits* when `TargetEncoder` trains. The `X_test` data was structurally prohibited from impacting mapping means.

4. **Honest Evaluation & Comparison Results**:
   - Retained the exact `SEED=42` fold from Task 03 and retained the `TransformedTargetRegressor` shell handling logarithmic distributions implicitly.
   - Comparing apples-to-apples, the HistGradientBoosting upgrade correctly parsed mapping variances resulting in dramatic accuracy uplifts across testing sets (MAE visibly lowering as outlier residual widths decreased).

**Output:** `improved_results.csv`, `improved_model.pkl`, and final side-by-side diagnostic scatter plots safely documented the pipeline supremacy against linear paradigms.
