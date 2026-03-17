# Prompt Log

> Paste each prompt you sent to the agent here, in order. Note what changed between iterations.

## Iteration 1
**Prompt:**
```
Prompt 4:
You are helping with a data science coursework project.
Inputs:
- Dataset: ../task_02_codex/output_02_codex/eda_cleaned.csv
- Baseline results: ../task_03_codex/output_03_codex/baseline_results.csv
- Baseline model: ../task_03_codex/output_03_codex/baseline_model.pkl
- EDA findings: ../task_02_codex/output_02_codex/eda_summary.md

Goal: predict nightly `price` (regression)

Task 04: Improving Performance.
Work entirely inside this notebook. Save all outputs to output_04_codex/.
SEED = 42

Deliverables:
1. Diagnose baseline weaknesses in markdown before coding.
2. Rank and justify improvement strategies, save to `output_04_codex/improvement_reasoning.md`.
3. Implement at least two improvement strategies.
4. Compare honestly with same metrics as Task 03.
5. Save `output_04_codex/improved_results.csv` and comparison chart.

Constraints:
- Test set must not influence training/tuning/feature decisions
- Show baseline alongside improved results
- Use only eda_cleaned.csv as dataset source
- Document decisions in markdown
- Relative paths only
```
**What happened:**
- Implemented two strategies and compared both:
  - GradientBoostingRegressor pipeline
  - RandomForestRegressor pipeline
- Saved outputs:
  - `output_04_codex/improvement_reasoning.md`
  - `output_04_codex/strategy_comparison.csv`
  - `output_04_codex/improved_results.csv`
  - `output_04_codex/improved_model.pkl`
  - `output_04_codex/baseline_vs_improved_metrics.png`
  - `output_04_codex/improved_predicted_vs_actual.png`
  - `output_04_codex/improved_residuals_plot.png`
  - `output_04_codex/improvement_report.md`

---

## Iteration 2
**Prompt:**
```
Remember to make Task 04 an ipynb file.
```
**What happened:**
- Converted Task 04 workflow to notebook files:
  - `task_04_improvement.ipynb`
  - `output_04_codex/task_04_improvement.ipynb`
- Confirmed baseline-vs-improved metrics in `output_04_codex/improved_results.csv`.

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

