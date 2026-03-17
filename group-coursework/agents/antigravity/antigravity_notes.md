# Agent Notes — Antigravity

> Evidence-based reflection on Antigravity's performance across all four tasks.
> All metrics, decisions, and failure observations are drawn directly from
> committed outputs in agents/antigravity/task_0X/outputs/.

---

## Task 01 — Data Ingestion

**What the agent helped with:**
Antigravity correctly identified and handled the dominant missingness pattern
in the dataset without prompting. The 20.56% missingness in `last_review` and
`reviews_per_month` was recognised as structurally linked — both columns are
missing for the same 10,052 listings that have never received a review. Rather
than defaulting to row deletion (which would have introduced ~20% response
bias and discarded structurally informative data), the agent applied semantic
sentinel imputation: `last_review` → `"No review"`, `reviews_per_month` → `0.0`.
This demonstrates understanding of MCAR missingness and the distinction between
missing-by-mechanism versus missing-at-random. The agent also correctly produced
all three required output files (`ingested.csv`, `schema_log.md`,
`missingness_report.md`) in the correct output directory using relative paths.
An additional `outlier_flags.txt` was generated proactively, flagging
`minimum_nights > 365`, `price <= 0`, and `price > 5000` without removing rows —
correctly deferring removal decisions to post-EDA stages to avoid premature
target-based filtering.

**What it failed at:**
The agent did not perform the train/test split before computing missingness
statistics. In Task 01 this is technically correct — ingestion operates on
the full dataset — but the agent did not make this boundary explicit in its
documentation, which created ambiguity about when the split would occur.
The `schema_log.md` also lacked min/max/cardinality columns that would have
strengthened the schema audit. The prompt required one correction to force
relative path usage — the agent's first draft used a hardcoded path.

**Iterations needed:**
2 — first prompt produced an absolute path (`C:\Users\...`); second prompt
added the relative path constraint explicitly and the agent corrected it.

**The prompt that worked best:**
```
You are helping with a UCL data science coursework benchmarking project.
Dataset: data/raw/AB_NYC_2019.csv (READ ONLY).
Task: Data Ingestion, Schema Checks, and Missingness Handling.
SEED = 42. All paths relative to repo root.
Save all outputs to agents/antigravity/task_01/outputs/
Required files: ingested.csv (zero nulls), schema_log.md, missingness_report.md.
Do not drop rows at this stage. Document every imputation decision with rationale.
Do not split train/test — that happens in Task 02.
```

**How I verified the output:**
Ran `evaluate.py` — scored 5/5 in 15 minutes. Manually inspected
`missingness_report.md` to confirm all four missing columns were addressed
with written justification. Verified `ingested.csv` had zero null values
using `df.isnull().sum().sum() == 0`.

---

## Task 02 — EDA

**What the agent helped with:**
Antigravity produced a substantive `eda_summary.md` that went beyond plot
descriptions to make modelling-relevant observations. Key findings included:
(1) the `price` distribution is severely right-skewed, requiring `log1p`
transformation for stable regression — this insight was carried forward
correctly into Task 03; (2) continuous numeric features (`minimum_nights`,
`availability_365`) exhibit weak linear correlation with price, which correctly
predicted that a linear baseline would underperform; (3) `room_type` and
`neighbourhood_group` were identified as the dominant structural price drivers,
leading to the correct engineering decision in Task 04 to apply TargetEncoder
to the high-cardinality `neighbourhood` column; (4) collinearity between
`reviews_per_month` and `number_of_reviews` was flagged, informing feature
selection decisions downstream. The agent also correctly capped `price` at
$1,000 and `minimum_nights` at 365 to limit noise from extreme outliers —
a decision it justified with reference to the EDA distribution plots.

**What it failed at:**
The agent did not explicitly assert that all EDA was computed on the training
split only. The `eda_cleaned.csv` output suggests some preprocessing was
applied during EDA — this required manual verification to confirm no test
data had been used. The written insights were strong but lacked quantitative
backing in places (e.g., "remarkably weak linear correlations" was not
accompanied by the actual Pearson r values from the heatmap).

**Iterations needed:**
1 — single prompt produced all required outputs. Manual review required
to verify the train/test boundary.

**The prompt that worked best:**
```
Load agents/antigravity/task_01/outputs/ingested.csv.
Split train/test 80/20 SEED=42 FIRST — before any analysis.
Perform EDA on training data only. Produce 3 plots: target distribution,
correlation heatmap, feature-target relationship.
Write 2-3 sentences of insight per plot in eda_summary.md.
Save figures as .png in outputs/. Relative paths only.
```

**How I verified the output:**
Inspected `eda_summary.md` for substantive written findings. Confirmed
three `.png` files saved correctly. Traced the notebook cell order to verify
the split preceded the first `value_counts()` call.

---

## Task 03 — Baseline Model

**What the agent helped with:**
Antigravity implemented a Ridge Regression baseline with a
`TransformedTargetRegressor` wrapper applying `log1p` to the target — a
methodologically sound decision informed directly by the Task 02 EDA finding
about price skewness. The full sklearn `Pipeline` architecture correctly
encapsulated the `ColumnTransformer` (StandardScaler on numerics,
OneHotEncoder on categoricals) with the estimator, ensuring the scaler and
encoder were fitted exclusively on `X_train` with no data leakage to
`X_val` or `X_test`. The `baseline_report.md` documented SEED=42, the 80/20
split, preprocessing decisions, and model limitations. Results: RMSE=115.18,
MAE=56.34, R²=0.236. The agent correctly identified in the limitations section
that Ridge's additive linear assumptions would fail to capture hyper-local
spatial interactions — directly motivating the Task 04 approach.

**What it failed at:**
The baseline only reported metrics on the test set — train and validation
metrics were not reported separately, making it impossible to assess whether
the model was overfitting. This is a gap in the evaluation harness. The
`baseline_results.csv` used `metric_name, value` columns rather than the
full `model_name, metric_name, metric_value, split` schema specified in the
group README, which required a correction before the comparative table
could be populated.

**Iterations needed:**
2 — first run produced correct model and metrics but missing train/val
split evaluation. Second prompt requested metrics per split explicitly.

**The prompt that worked best:**
```
Build a Ridge Regression baseline on ingested.csv. Split 80/20 SEED=42.
Use TransformedTargetRegressor with log1p on the target.
Fit all preprocessing inside a Pipeline on train only — never the full dataset.
Report RMSE, MAE, R² on train, val, and test splits separately.
Save to outputs/baseline_results.csv with columns: metric_name, value.
Save model as outputs/model.pkl. Write baseline_report.md. SEED=42 throughout.
```

**How I verified the output:**
Loaded `model.pkl` and confirmed it was a fitted Pipeline object. Checked
`baseline_results.csv` for correct column headers and numeric values.
Cross-checked RMSE=115.18 against manual computation on the test set.

---

## Task 04 — Improving Performance

**What the agent helped with:**
Antigravity made a methodologically sophisticated improvement: it replaced
Ridge with `HistGradientBoostingRegressor` (a gradient-boosted tree ensemble)
and introduced `TargetEncoder` for the high-cardinality `neighbourhood` column,
which had been explicitly excluded from the baseline due to cardinality concerns.
The key distinction-level decision was the leakage handling: sklearn's
`TargetEncoder` applies cross-validation smoothing internally during `fit()`,
preventing test-set target values from informing the training-set encoding —
a subtle leakage pattern that many implementations get wrong. The agent
documented this explicitly in the leakage check section of `improvement_report.md`.
Results: RMSE improved from 115.18 → 106.07 (-7.91%), MAE from 56.34 → 50.59
(-10.21%), R² from 0.236 → 0.352 (+49.2% relative). The improvement is
meaningful — a ~$9 reduction in typical prediction error is practically
significant for Airbnb pricing decisions and well above the noise threshold.

**What it failed at:**
The `improved_results.csv` used a different schema (`metric_name,
baseline_value, improved_value, delta_pct`) compared to the baseline CSV
(`metric_name, value`). While the delta_pct column is informative, the
schema inconsistency means the two files cannot be joined directly for
the comparative analysis table. The agent also did not document any
approaches that failed — only the successful strategy is described. A
distinction-level report requires evidence of what was tried and rejected,
not just what worked.

**Iterations needed:**
1 — single prompt produced the improved model and all required outputs.
No leakage was detected on inspection.

**The prompt that worked best:**
```
Improve on the Task 03 Ridge baseline. Use HistGradientBoostingRegressor.
Apply TargetEncoder to the neighbourhood column — inside the Pipeline
to prevent leakage. Keep SEED=42. Show baseline vs improved metrics
side by side. Save improved_model.pkl and improvement_report.md explaining
what was tried, what worked, and confirming no leakage was introduced.
```

**How I verified the output:**
Checked that `TargetEncoder` was inside the Pipeline `fit()` call, not
applied before the split. Verified `improved_model.pkl` was a fitted object.
Confirmed delta values matched manual computation from the two CSVs.
Inspected the leakage check section of `improvement_report.md`.

---

## Overall Reflection — Antigravity

**Strengths of this tool:**
- Strong at structured, multi-output tasks where the expected files and
  formats are specified upfront. When given explicit output file names and
  column schemas, Antigravity consistently produced correctly named files
  in the right directories.
- Demonstrated genuine methodological reasoning, not just code generation:
  the choice to use `TransformedTargetRegressor` in Task 03 was directly
  informed by the Task 02 EDA finding about price skewness; the TargetEncoder
  leakage handling in Task 04 showed awareness of a subtle cross-contamination
  pattern that simpler agents missed.
- Faster than expected for Tasks 01 and 02 (15 min and ~20 min respectively),
  with correct outputs on first or second attempt.
- Produced unsolicited but useful supplementary outputs (`outlier_flags.txt`,
  `eda_cleaned.csv`, `model_selection_reasoning.md`) that added analytical
  depth beyond the minimum spec.

**Weaknesses:**
- Inconsistent output schemas across tasks: `baseline_results.csv` and
  `improved_results.csv` use different column structures, breaking
  cross-task joins. A schema-consistent agent would be more valuable in
  production pipelines.
- Did not document failed approaches in Task 04 — only reported the
  successful strategy. For a benchmarking study this is a significant gap:
  failure evidence is more diagnostic than success evidence.
- Required explicit relative path constraints — the first draft of Task 01
  used an absolute path, which would have broken reproducibility on any
  other machine.
- Train/val/test split evaluation was incomplete in Task 03 on the first
  attempt — only test metrics were reported, obscuring the overfitting picture.

**Would I use it again for DS work?**
Yes, conditionally. Antigravity is well-suited to structured data science
pipeline tasks where the output format, file names, and evaluation criteria
are specified upfront. It performs well on ingestion, EDA, and modelling
tasks when given detailed guardrails. It is less reliable for open-ended
analysis or tasks requiring documentation of the full decision trail
(including failed approaches). The recommended workflow is: specify exact
output schemas and filenames in the prompt, require explicit train/test
boundary documentation, and always verify leakage discipline manually
before treating outputs as production-ready.
