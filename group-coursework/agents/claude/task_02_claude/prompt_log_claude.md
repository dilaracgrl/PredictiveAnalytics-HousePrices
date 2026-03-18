# Prompt Log — Task 02: Exploratory Data Analysis

## Iteration 1
**Prompt:**
```
Using outputs_claude/ingested.csv from task_01_claude, perform EDA on the
training data only — do not create or reference a test split.

Produce at least 3 plots:
1. Target variable (price) distribution — raw and log1p-transformed.
2. A feature correlation heatmap (numeric features vs price).
3. At least one plot showing a feature's relationship with price
   (e.g. median price by room_type, or by neighbourhood_group).

After each plot, write 2–3 sentences of interpretation in a markdown cell.
Save each figure as a .png in outputs_claude/.
Write a summary of key findings to outputs_claude/eda_summary.md —
include which features are most predictive, any data quality issues found,
and recommendations for preprocessing in Task 03.
Save the cleaned dataset (outliers removed) as outputs_claude/eda_cleaned.csv.
Use only relative paths. Clear all output cells before saving the notebook.
```
**What happened:**
The agent produced 9 plots covering price distribution (raw and log), correlation heatmap, median price by borough, by room type, geographic scatter, neighbourhood rankings, pairplot, and categorical counts. Each plot had accompanying markdown interpretation. `eda_summary.md` was produced with clear recommendations including log1p transform, target encoding for `neighbourhood`, and geo-clustering for Task 04. `eda_cleaned.csv` was saved with price capped at the 99th percentile and `minimum_nights` clipped at 30. No test split was created. Notebook passed all checks — scored 5/5.

---

## Iteration 2
**Prompt:**
```
The eda_summary.md looks good but please add a section specifically recommending
feature engineering steps for Task 04 — include neighbourhood target encoding,
geo-cluster features from lat/lon, interaction terms, and log transforms for
skewed numeric features. This will serve as the plan for Task 04.
```
**What happened:**
The agent appended a "Feature Engineering Recommendations for Task 04" section to `eda_summary.md` listing 5 specific engineering steps with justification. This section was later used directly as the implementation plan in Task 04.
