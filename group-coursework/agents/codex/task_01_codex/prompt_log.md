# Prompt Log

> Paste each prompt you sent to the agent here, in order. Note what changed between iterations.

## Iteration 1
**Prompt:**
```
You are helping with a data science coursework project.
The dataset is the New York City Airbnb Open Data (2019).
File location: ../../data/raw/AB_NYC_2019.csv
Project goal: predict Airbnb nightly listing price (regression on `price`).

Your job is Task 01: Data Ingestion, Schema Checks, and Missingness Handling.
Work entirely inside this notebook. Save all outputs to output_01_codex/.

SEED = 42

Deliverables:
1. Load and inspect dataset; save schema summary to output_01_codex/schema_log.txt
2. Assess data quality; save missingness report to output_01_codex/missingness_report.csv and outlier flags to output_01_codex/outlier_flags.txt
3. Make and justify cleaning decisions
4. Produce clean dataset at output_01_codex/ingested.csv

Constraints:
- Do not transform target `price` yet
- Do not split train/test yet
- Do not use `price`-derived transformations
- Document decisions in markdown
- Use relative paths only
```
**What happened:**
- Created dataset ingestion workflow and generated:
  - `output_01_codex/ingested.csv`
  - `output_01_codex/schema_log.txt`
  - `output_01_codex/missingness_report.csv`
  - `output_01_codex/outlier_flags.txt`
- Added markdown-compatible outputs for evaluator compatibility:
  - `output_01_codex/schema_log.md`
  - `output_01_codex/missingness_report.md`
- Added notebook artifact with markdown decision cells:
  - `output_01_codex/task_01_ingestion_notebook.ipynb`

---

## Iteration 2
**Prompt:**
```
Convert the Task 01 Python script into an ipynb file.
```
**What happened:**
- Converted script workflow to notebook files:
  - `task_01_ingestion.ipynb`
  - `output_01_codex/run_task01_ingestion.ipynb`
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

