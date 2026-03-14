# Task 02 — Exploratory Data Analysis (EDA)

## Objective
Explore the dataset and generate insight-driven plots. Every plot must be accompanied by written interpretation — plots without commentary do not count.

## Inputs
| File | Location |
|------|----------|
| Ingested dataset | `agents/<agent>/task_01/outputs/ingested.csv` |

## Expected Outputs
| File | Location | Description |
|------|----------|-------------|
| `notebook_template.ipynb` (completed) | `agents/<agent>/task_02/outputs/` | EDA notebook with plots and commentary |
| `eda_summary.md` | `agents/<agent>/task_02/outputs/` | Written summary of key insights |
| Plot files (`*.png`) | `agents/<agent>/task_02/outputs/` | At least 3 saved figures |

## Rubric (5 points)

| Criterion | Points | Description |
|-----------|--------|-------------|
| At least 3 meaningful plots produced | 1 | Target distribution, feature correlation heatmap, feature-target relationship |
| Target variable distribution examined | 1 | Plot + 2–3 sentence interpretation |
| Feature–target relationship explored | 1 | At least one feature's relationship with the target plotted and interpreted |
| Insights written in markdown | 1 | `eda_summary.md` contains substantive written findings (not just plot descriptions) |
| No test set used during EDA | 1 | All analysis performed on training data only |

## Suggested Agent Prompt
```
Using ingested.csv, perform EDA. Produce at least 3 plots:
1. Target variable distribution.
2. A feature correlation heatmap.
3. One plot showing a feature's relationship with the target.
After each plot, write 2-3 sentences of insight in markdown.
Do not load or reference the test split.
Save each figure as a .png in outputs/.
Write a summary of key findings to outputs/eda_summary.md.
Use only relative paths. Clear all output cells before saving the notebook.
```

## Known Failure Modes
- Plotting test set distributions — this is leakage; EDA must use training data only.
- Generating plots with no textual interpretation.
- Hallucinating feature names that do not exist in the dataset.
- Committing notebook with output cells still present.

## How to Score
```bash
python tasks/task_02_eda/evaluate.py \
  --agent agents/<agent>/task_02/ \
  --name <your_name> \
  --tool "<Tool Name>" \
  --time <minutes> \
  --notes "<brief notes>" \
  --failure "<failure mode or 'none'>"
```
