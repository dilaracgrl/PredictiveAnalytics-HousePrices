# Task 04 — Improving Performance

## Objective
Improve on the baseline via feature engineering, hyperparameter tuning, or a model change. The improvement must be demonstrable and free of new leakage.

## Inputs
| File | Location |
|------|----------|
| Ingested dataset | `agents/<agent>/task_01/outputs/ingested.csv` |
| Baseline results | `agents/<agent>/task_03/outputs/baseline_results.csv` |
| Baseline model | `agents/<agent>/task_03/outputs/model.pkl` |

## Expected Outputs
| File | Location | Description |
|------|----------|-------------|
| `improved_results.csv` | `agents/<agent>/task_04/outputs/` | Baseline vs improved metrics side by side |
| `improved_model.pkl` | `agents/<agent>/task_04/outputs/` | Serialised improved model |
| `improvement_report.md` | `agents/<agent>/task_04/outputs/` | What was tried, why, and whether it worked |

## Rubric (5 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| Baseline comparison included | 1 | `improved_results.csv` shows baseline and improved scores side by side |
| At least one improvement technique applied | 1 | Feature engineering, hyperparameter tuning, or a different model — clearly stated |
| No new leakage introduced | 1 | All new preprocessing steps still fitted on train data only |
| Improvement is meaningful | 1 | Delta exceeds plausible noise (not a rounding-error "improvement") |
| Approach justified in markdown | 1 | `improvement_report.md` explains what was tried, the result, and why it worked or didn't |

## Suggested Agent Prompt
```
Starting from the baseline in task_03, improve model performance.
Try at least one of: feature engineering, hyperparameter tuning, or a different model.
Show baseline vs improved metrics side by side in outputs/improved_results.csv
with columns: metric_name, baseline_value, improved_value.
Save the improved model as outputs/improved_model.pkl.
Justify your approach in outputs/improvement_report.md — explain what you tried,
what worked, and confirm that no leakage was introduced.
Use SEED = 42. Relative paths only.
```

## Known Failure Modes
- Tuning on the test set (choose hyperparameters using cross-validation on training data only).
- Reporting improvement without a proper baseline comparison.
- Feature engineering that leaks target information (e.g. encoding target mean before split).
- Marginal delta (< 0.1%) claimed as a meaningful improvement.

## How to Score
```bash
python tasks/task_04_improving_performance/evaluate.py \
  --agent agents/<agent>/task_04/ \
  --name <your_name> \
  --tool "<Tool Name>" \
  --time <minutes> \
  --notes "<brief notes>" \
  --failure "<failure mode or 'none'>"
```
