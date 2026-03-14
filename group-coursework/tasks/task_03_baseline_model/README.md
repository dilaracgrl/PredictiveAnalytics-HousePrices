# Task 03 — Baseline Model

## Objective
Train a simple baseline model with a proper evaluation harness. This establishes the performance floor that task_04 must demonstrably beat.

## Inputs
| File | Location |
|------|----------|
| Ingested dataset | `agents/<agent>/task_01/outputs/ingested.csv` |

## Expected Outputs
| File | Location | Description |
|------|----------|-------------|
| `baseline_results.csv` | `agents/<agent>/task_03/outputs/` | Per-metric scores on the test set |
| `model.pkl` | `agents/<agent>/task_03/outputs/` | Serialised trained model |
| `baseline_report.md` | `agents/<agent>/task_03/outputs/` | Model choice, split details, seed, preprocessing steps |

## Rubric (5 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| Train/test split done correctly | 1 | 80/20 split, `SEED = 42`, documented in `baseline_report.md` |
| Preprocessing fitted on train only | 1 | Scaler/encoder fitted on training data — never on the full dataset |
| At least two metrics reported | 1 | e.g. accuracy + F1, or RMSE + R² — not just a single metric |
| Results saved to CSV | 1 | `baseline_results.csv` present with metric names and values |
| Random seed documented | 1 | `SEED = 42` appears in the script and in `baseline_report.md` |

## Suggested Agent Prompt
```
Build a baseline model on ingested.csv. Split 80/20 with SEED=42.
Fit all preprocessing (scaling, encoding) on the train set only — never the full dataset.
Report accuracy, F1, and AUC on the test set.
Save results to outputs/baseline_results.csv with columns: metric_name, value.
Save the trained model as outputs/model.pkl.
Write a baseline_report.md explaining the model choice, split, seed, and preprocessing steps.
Use SEED = 42 throughout. Relative paths only.
```

## Known Failure Modes
- `StandardScaler` or encoder fitted before the train/test split.
- Only reporting accuracy on imbalanced classes.
- Not setting or documenting `SEED = 42`.
- Saving `baseline_results.csv` without column headers.

## How to Score
```bash
python tasks/task_03_baseline_model/evaluate.py \
  --agent agents/<agent>/task_03/ \
  --name <your_name> \
  --tool "<Tool Name>" \
  --time <minutes> \
  --notes "<brief notes>" \
  --failure "<failure mode or 'none'>"
```
