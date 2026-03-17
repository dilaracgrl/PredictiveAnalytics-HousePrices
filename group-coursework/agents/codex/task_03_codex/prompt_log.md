# Prompt Log

> Paste each prompt you sent to the agent here, in order. Note what changed between iterations.

## Iteration 1
**Prompt:**
```
Prompt 3:
You are helping with a data science coursework project.
Inputs:
- ../task_02_codex/output_02_codex/eda_cleaned.csv
- ../task_02_codex/output_02_codex/eda_summary.md
Goal: predict Airbnb nightly `price` (regression)

Task 03: Baseline Model Training and Evaluation Harness.
Work entirely inside this notebook. Save all outputs to output_03_codex/.
SEED = 42

Deliverables:
1. Write model choice reasoning first and save `output_03_codex/model_selection_reasoning.md`
2. Create reproducible train/test split
3. Build preprocessing fit on train only
4. Train simple baseline model
5. Report RMSE, MAE, R2 + diagnostic plots
6. Save results and model artifacts for Task 04

Constraints:
- Use SEED=42 for split/model randomness
- No preprocessing fit on full data/test
- No hyperparameter tuning
- Document decisions in markdown
- Relative paths only
```
**What happened:**
- Implemented baseline training pipeline with train-only preprocessing.
- Saved:
  - `output_03_codex/model_selection_reasoning.md`
  - `output_03_codex/baseline_results.csv`
  - `output_03_codex/baseline_pipeline.pkl`
  - `output_03_codex/baseline_model.pkl`
  - `output_03_codex/model.pkl`
  - `output_03_codex/predicted_vs_actual.png`
  - `output_03_codex/residuals_plot.png`
  - `output_03_codex/baseline_report.md`

---

## Iteration 2
**Prompt:**
```
Remember to make Task 03 an ipynb file.
```
**What happened:**
- Converted Task 03 workflow to notebook files:
  - `task_03_baseline.ipynb`
  - `output_03_codex/task_03_baseline.ipynb`
- Ensured notebook outputs are cleared.

---
## Iteration 3
**Prompt:**
```
Update paths to reflect codex naming:
- task folders: task_0X_codex
- output folders: output_0X_codex
```
**What happened:**
- Updated the prompt log and file-path references to the renamed Codex structure.
- Confirmed paths now reference `task_0X_codex` and `output_0X_codex` consistently.

