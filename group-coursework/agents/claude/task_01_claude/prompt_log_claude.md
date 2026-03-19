# Prompt Log — Task 01: Data Ingestion

> Rules preamble sent before the prompt (from CONTRIBUTING.md instructions):
> Work only inside agents/claude/task_01/ — outputs to outputs/ — relative paths only —
> SEED = 42 — clear notebook outputs before commit — justify every decision in markdown.

## Iteration 1
**Prompt:**
```
You are helping with a data science coursework project.
The dataset is the New York City Airbnb Open Data (2019).
File location: ../../data/raw/AB_NYC_2019.csv
Project goal: predict Airbnb nightly listing price (regression on `price`).

Your job is Task 01: Data Ingestion, Schema Checks, and Missingness Handling.
Work entirely inside this notebook. Save all outputs to outputs/.

SEED = 42

--- WHAT YOU NEED TO DELIVER ---

1. Load and inspect the dataset
   Understand what you are working with before writing any cleaning code.
   What are the columns? What are their types? What does each one represent?
   Save a schema summary to outputs/schema_log.txt

2. Assess data quality
   Identify every quality issue you can find: missing values, suspicious types,
   columns that cannot be useful for modelling, potential outliers.
   Produce a missingness report and save it to outputs/missingness_report.csv
   Flag any columns with outliers or suspicious values in outputs/outlier_flags.txt

3. Make and justify cleaning decisions
   For each issue you find, decide what to do about it and WHY.
   There is no single correct answer — your reasoning is what matters.
   Consider: which columns are worth keeping? What does missingness actually mean
   in this dataset — is it a data error or does it mean something real?
   What should you do with extreme values in price? In minimum_nights?

4. Produce a clean dataset
   Apply your decisions and save the result to outputs/ingested.csv
   Confirm the output is free of the issues you identified.

--- CONSTRAINTS (non-negotiable) ---

- Do NOT transform the target variable `price` yet — that happens in Task 03
- Do NOT split into train/test yet — that happens in Task 03
- Do NOT apply any transformation that uses information derived from `price`
- Every decision must be written up in a markdown cell with a clear justification
- Save all outputs to outputs/ using relative paths only
```
**What happened:**
The agent produced the notebook and it ran without errors. However, `ingested.csv` contained **0 rows**. Despite the "relative paths only" constraint, the path `../../data/raw/AB_NYC_2019.csv` resolved incorrectly — VS Code sets the Jupyter kernel's working directory to the project root, not the `task_01_claude/` folder, so the relative path pointed one level too high and found no file. `pd.concat([])` silently returned an empty DataFrame with the correct schema; no error was raised. Caught by manually checking file size (~10KB instead of ~60MB) and noticing "Loaded: 0 rows" in the output.

The agent produced `schema_log.txt`, `missingness_report.csv`, and `outlier_flags.txt` but the missingness report had no per-column written justification for each decision — just counts and percentages.

---

## Iteration 2
**Prompt:**
```
The notebook produced 0 rows in ingested.csv. The path ../../data/raw/ resolves
incorrectly in VS Code — the kernel runs from the project root, not the notebook
folder. Fix the path using pathlib resolved relative to the notebook file itself,
or use an explicit path from the repo root. Also add a guard: if the file is not
found, raise a FileNotFoundError immediately rather than silently loading 0 rows.
Re-run and confirm the row count is 48,895.
```
**What happened:**
The agent fixed path resolution and added the guard. Re-running confirmed 48,895 rows. All outputs were saved correctly. Score: 2/5 — `schema_log.txt` was accepted but the missingness report lacked per-column written justification, and the manual check on handling strategy documentation failed.
