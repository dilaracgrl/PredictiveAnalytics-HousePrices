# Task 01 — Data Ingestion

## Objective
Load the dataset via the Kaggle API, run schema checks, and handle missingness. Produce a clean, validated CSV ready for EDA.

## Inputs
| File | Location |
|------|----------|
| Raw dataset | `data/raw/` (downloaded via `data/download_data.py`) |

## Expected Outputs
| File | Location | Description |
|------|----------|-------------|
| `ingested.csv` | `agents/<agent>/task_01/outputs/` | Schema-validated, missingness-handled dataset |
| `schema_log.md` | `agents/<agent>/task_01/outputs/` | Column names, dtypes, row count |
| `missingness_report.md` | `agents/<agent>/task_01/outputs/` | Count and % missing per column, handling strategy |

## Rubric (5 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| Dataset loads without error | 1 | Script runs end-to-end without exceptions |
| Schema validated | 1 | `schema_log.md` contains column names, dtypes, and row count |
| Missingness report produced | 1 | `missingness_report.md` lists count and % missing per column |
| Handling strategy documented and applied | 1 | Every imputation or drop decision is justified in markdown |
| Output saved correctly | 1 | `ingested.csv` present in `outputs/` and passes automated checks |

## Suggested Agent Prompt
```
Load the dataset from ../../data/raw/. Check the schema: print column names,
dtypes, and shape. Produce a missingness report (count and % per column).
Apply a handling strategy and justify every decision in markdown.
Save the result to outputs/ingested.csv.
Also save a schema_log.md (column names, dtypes, row count) and a
missingness_report.md (count + % per column + handling strategy).
Use SEED = 42 for any random operations. Use only relative paths.
```

## Known Failure Modes
- Filling missing values before train/test split — this is leakage; document that handling is applied to the full ingested set but that any imputation fitted on training data only will happen in task_03.
- Silently dropping rows without logging how many were removed.
- Hardcoding absolute file paths.
- Using a library not in `requirements.txt`.

## How to Score
```bash
python tasks/task_01_data_ingestion/evaluate.py \
  --agent agents/<agent>/task_01/ \
  --name <your_name> \
  --tool "<Tool Name>" \
  --time <minutes> \
  --notes "<brief notes>" \
  --failure "<failure mode or 'none'>"
```
