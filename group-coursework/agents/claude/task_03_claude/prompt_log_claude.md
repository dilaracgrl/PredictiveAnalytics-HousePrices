# Prompt Log — Task 03: Baseline Model

## Iteration 1
**Prompt:**
```
You are helping with a data science coursework project.
The dataset is the New York City Airbnb Open Data (2019).
Your input:    ../task_02/outputs/eda_cleaned.csv
EDA findings:  ../task_02/outputs/eda_summary.md
Project goal:  predict Airbnb nightly listing price (regression on `price`).

Your job is Task 03: Baseline Model Training and Evaluation Harness.
Work entirely inside this notebook. Save all outputs to outputs/.

SEED = 42  ← set at the top, use for the split, the model, and anything random

--- WHAT YOU NEED TO DELIVER ---

1. Reason about your model choice BEFORE writing any modelling code
   Read your EDA summary first.
   What does the data tell you about the right approach?
   What model makes sense as a baseline — and why that model specifically?
   What are its known limitations for this problem?
   Write this reasoning in a markdown cell and save it to
   outputs/model_selection_reasoning.md
   Your reasoning will be compared against other agents' reasoning in the group report.

2. Set up a sound train/test split
   Split the data appropriately for a regression problem.
   Justify your split strategy and proportions in markdown.
   Make sure the split is reproducible.

3. Build a preprocessing pipeline
   Decide what preprocessing this data needs before modelling.
   Whatever you include, it must be fitted on the train set only.
   Justify your pipeline choices in markdown.

4. Train your baseline model
   Keep it genuinely simple — the baseline exists to be beaten in Task 04,
   not to be the best possible model.
   Document your choices clearly.

5. Evaluate rigorously
   Choose your evaluation metrics carefully.
   Think about the distribution of `price` — what does this mean for which
   metrics are meaningful and which are misleading?
   Report at minimum: RMSE, MAE, and R².
   Produce diagnostic plots: predicted vs actual, and residuals.
   Save plots to outputs/.

6. Save everything needed for Task 04 to build on
   Save results to outputs/baseline_results.csv
   Save the fitted pipeline and model as .pkl files to outputs/

--- CONSTRAINTS (non-negotiable) ---

- SEED=42 must be used for the split and the model
- Preprocessing must be fitted on train data only — never on the full dataset or test set
- Do NOT tune hyperparameters — this is a baseline, save improvement for Task 04
- Document every decision in a markdown cell
- Save all outputs to outputs/ using relative paths only
```
**What happened:**
The agent read the EDA summary first and reasoned in markdown that Ridge Regression on log1p(price) was the right baseline — linear model for interpretability, log transform to handle skewness, Ridge over OLS for stability after one-hot encoding. All preprocessing inside a scikit-learn Pipeline fitted on `X_train` only. Results saved to `baseline_results.csv` (train and test rows, columns: split, RMSE_USD, MAE_USD, R2_log, R2_raw). Test RMSE = 83.32, R²_log = 0.549. `model_selection_reasoning.md` documented rationale, limitations, and features used. `neighbourhood` excluded (200+ levels) with explicit justification — deferred to Task 04.

Output files were named `baseline_pipeline.pkl` (not `model.pkl`) and `model_selection_reasoning.md` (not `baseline_report.md`) — one automated check failed on filename. Score: 4/5.

---

## Iteration 2
**Prompt:**
```
The baseline_results.csv only has test-set metrics. Please also add a train-set
row using the same columns (split, RMSE_USD, MAE_USD, R2_log, R2_raw) so we
can check for overfitting and have a cleaner comparison table for Task 04.
```
**What happened:**
Train row added. Train RMSE = 83.65, Test RMSE = 83.32 — near-identical, confirming no overfitting. Results file updated.
