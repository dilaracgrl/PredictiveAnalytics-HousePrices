# Prompt Log — Task 01: Data Ingestion

## Iteration 1
**Prompt:**
```
Load the dataset from ../../data/raw/. Check the schema: print column names,
dtypes, and shape. Produce a missingness report (count and % per column).
Apply a handling strategy and justify every decision in markdown.
Save the result to outputs/ingested.csv.
Also save a schema_log.md (column names, dtypes, row count) and a
missingness_report.md (count + % per column + handling strategy).
Use SEED = 42 for any random operations. Use only relative paths.
```
**What happened:**
The agent produced the notebook and it ran without errors. However, the output `ingested.csv` contained **0 rows**. The path `../../data/raw/` resolved incorrectly because VS Code sets the Jupyter kernel's working directory to the project root, not the `task_01_claude/` folder. The glob found zero CSVs and `pd.concat([])` silently returned an empty DataFrame with the correct schema. The parquet-equivalent file was only ~10KB instead of the expected ~60MB. Caught by manually checking row counts and file size — no error was raised at any point.

The agent also saved a `missingness_report.csv` instead of `missingness_report.md`, and did not produce a `schema_log.md` at all.

---

## Iteration 2
**Prompt:**
```
The notebook produced 0 rows in ingested.csv. The path ../../data/raw/ is
wrong — VS Code runs the kernel from the project root, not the notebook folder.
Fix the path using pathlib to resolve relative to __file__ or use an absolute
CWD-agnostic path. Also add a guard: if glob finds zero CSV files, raise a
FileNotFoundError immediately rather than silently concatenating an empty list.
Re-run and confirm row count is 48895.
```
**What happened:**
The agent rewrote the path resolution using `Path(__file__).resolve().parent` and added the `FileNotFoundError` guard. Re-running confirmed 48,895 rows loaded correctly. The `ingested.csv` output passed schema validation. The `missingness_report.csv` was retained (accepted by evaluate.py) but `schema_log.md` was not produced in this iteration — this caused the task 01 score to be 2/5 (schema_log check failed, and the missingness report lacked per-column written justification for each decision).
