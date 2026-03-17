# Prompt Log

> Paste each prompt you sent to the agent here, in order. Note what changed between iterations.

## Iteration 1
**Prompt:**
```
Prompt 2:
You are helping with a data science coursework project.
Dataset: New York City Airbnb Open Data (2019)
Input: ../task_01_codex/output_01_codex/ingested.csv
Goal: predict `price` (regression)

Task 02: EDA and Insight Generation.
Work entirely inside this notebook. Save all outputs to output_02_codex/.
SEED = 42

Deliverables:
1. Explore target variable `price` thoroughly and write conclusions.
2. Explore features (geo, categorical location, review/availability metrics).
3. Analyze relationships between features and price beyond simple correlations.
4. Resolve remaining quality issues and save `output_02_codex/eda_cleaned.csv`.
5. Write EDA summary and save `output_02_codex/eda_summary.md`.

Constraints:
- Read from ingested.csv only
- No train/test split
- No held-out data
- Every plot has title, axis labels, and markdown interpretation
- Relative paths only
```
**What happened:**
- Built EDA workflow and generated multiple plots in `output_02_codex/`.
- Saved `output_02_codex/eda_cleaned.csv` and `output_02_codex/eda_summary.md`.
- Added markdown interpretation sections in notebook version.

---

## Iteration 2
**Prompt:**
```
Remember to make Task 02 an ipynb file.
```
**What happened:**
- Created notebook artifacts:
  - `task_02_eda.ipynb`
  - `output_02_codex/task_02_eda.ipynb`
- Kept output cells cleared.

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

