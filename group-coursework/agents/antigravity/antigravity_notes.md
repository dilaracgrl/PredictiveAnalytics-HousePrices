# Agent Notes: Antigravity

All observations below are drawn from committed output files in
agents/antigravity/task_0X/outputs/ and cross-referenced against
results/scores.csv. Where comparisons to Claude and Codex are made,
they reference the same committed outputs in their respective agent folders.

---

## Task 01: Data Ingestion

**What the agent helped with:**

Antigravity correctly handled the structural missingness pattern in the
dataset. The 20.56% missingness rate in `last_review` and `reviews_per_month`
affects the same 10,052 listings: those with no review history. Geron (2019,
Ch.2) warns against data snooping bias, noting that any inspection of test-set
distributions before the train/test split can contaminate model selection.
Antigravity avoided this by treating ingestion as a pre-split operation and
applying semantic sentinel imputation rather than row deletion. Dropping
10,052 rows would have removed roughly 20% of the dataset and introduced
response bias by systematically excluding newer or less popular listings.
Instead, `last_review` nulls were filled with the string "No review" and
`reviews_per_month` nulls with 0.0, preserving the structural signal that a
missing review frequency is meaningfully different from a low one.

Antigravity also produced `outlier_flags.txt` without being asked, flagging
`minimum_nights > 365`, `price <= 0`, and `price > 5000`. Rows were not
removed at this stage, which is correct: Geron (2019, Ch.2) recommends
creating a test set before doing any further exploration, and premature
target-based filtering (dropping `price = 0` rows before EDA) would bias
the target distribution visible to the analyst.

Compared to Claude (Task 01 score: 2/5, 20 min), Antigravity scored 5/5
in 15 minutes. The score difference is traceable to the manual check:
Claude's `missingness_report.md` passed automated keyword checks for the
word "strategy" but lacked written justification for each imputation decision.
Antigravity's report documented rationale per column. Codex also scored 5/5
but took 25 minutes. Antigravity was the fastest to a full score.

**What it failed at:**

The `schema_log.md` covered column names and dtypes but omitted min, max,
and cardinality values. A complete schema audit, as described in Geron
(2019, Ch.2) under attribute investigation, should quantify value ranges
and count distinct categories for each column. Without min/max on `price`
and `minimum_nights`, downstream tasks had to rediscover the outlier ranges
independently. This gap required manual correction in Task 02.

The first prompt output contained a hardcoded absolute path
(`C:\Users\Caroline Kelly\...`). This is a structural limitation of
IDE-embedded agents: Antigravity inherits the working directory from the
VS Code session rather than the repo root. It is not a one-off error but
a predictable failure mode for any team member who opens the project
from a different machine. The fix required a second prompt with an
explicit relative path constraint. This is logged in `task_01/prompt_log.md`.

**Iterations needed:**
2. First prompt: absolute path. Second prompt: added relative path
constraint. Output was correct on the second attempt.

**The prompt that worked best:**
```
You are helping with a UCL data science coursework benchmarking project.
Dataset: data/raw/AB_NYC_2019.csv (READ ONLY).
Task: Data Ingestion, Schema Checks, and Missingness Handling.
SEED = 42. All paths relative to repo root.
Save all outputs to agents/antigravity/task_01/outputs/
Required files: ingested.csv (zero nulls), schema_log.md, missingness_report.md.
Do not drop rows at this stage. Document every imputation decision with rationale.
Do not split train/test -- that happens in Task 02.
```

**How I verified the output:**
Ran evaluate.py: 5/5 in 15 minutes. Manually checked `missingness_report.md`
against all four missing columns. Confirmed `df.isnull().sum().sum() == 0`
on the saved `ingested.csv`.

---

## Task 02: EDA and Insight Generation

**What the agent helped with:**

The `eda_summary.md` made modelling-relevant observations rather than
restating what the plots showed. Antigravity identified that the `price`
distribution is heavily right-skewed and recommended `log1p` transformation
before regression. This is consistent with Geron (2019, Ch.2), which notes
that skewed attributes can be transformed to reduce the influence of
extreme values on distance-based and gradient-based methods. The
recommendation was carried forward into Task 03 via `TransformedTargetRegressor`.

Antigravity identified that continuous numeric features (`minimum_nights`,
`availability_365`) had weak linear correlation with price, while categorical
features (`room_type`, `neighbourhood_group`) were the primary structural
drivers. This prediction proved correct: the Ridge baseline in Task 03 achieved
R2 = 0.236, consistent with a dataset where the dominant signal is categorical
and linear models are poorly suited without encoding the high-cardinality
`neighbourhood` column.

The agent also flagged collinearity between `reviews_per_month` and
`number_of_reviews`, which informed feature selection in Task 03.

**What it failed at:**

The `eda_cleaned.csv` output in the Task 02 folder indicates preprocessing
was applied during the EDA phase. It was not immediately clear from the
notebook structure whether this preprocessing was applied before or after
the train/test split. Geron (2019, Ch.2) is explicit: "before you look at
the data any further, you need to create a test set, put it aside, and never
look at it." A summary statistic computed on the full dataset before the
split is data snooping bias, even if no model is trained. Manual inspection
of cell order was required to confirm the split preceded any `value_counts()`
or `.describe()` call.

The EDA insights quoted qualitative descriptions ("remarkably weak linear
correlations") without citing the actual Pearson r values from the heatmap.
This makes the claims harder to reproduce and harder to cross-check against
the correlation matrix in the committed plot file.

**Iterations needed:**
1. Single prompt produced all required output files. Manual review was
needed to verify the leakage boundary.

**The prompt that worked best:**
```
Load agents/antigravity/task_01/outputs/ingested.csv.
Split train/test 80/20 SEED=42 FIRST -- before any analysis.
Perform EDA on training data only. Produce 3 plots: target distribution,
correlation heatmap, feature-target relationship.
Write 2-3 sentences of insight per plot in eda_summary.md.
Save figures as .png in outputs/. Relative paths only.
```

**How I verified the output:**
Checked `eda_summary.md` for written findings beyond plot descriptions.
Confirmed three `.png` files were saved. Traced notebook cell order to
confirm the split appeared before the first `value_counts()` call.

---

## Task 03: Baseline Model

**What the agent helped with:**

The baseline uses Ridge Regression wrapped in `TransformedTargetRegressor`
with `log1p` applied to the target. This directly addresses the skewness
observation from Task 02. The full sklearn `Pipeline` encapsulates
`ColumnTransformer` (StandardScaler on numeric columns, OneHotEncoder on
`neighbourhood_group` and `room_type`) with the estimator, so the scaler
and encoder are fitted on X_train only. Geron (2019, Ch.2) describes this
pattern precisely: fitting the full pipeline on training data and calling
`.transform()` on test data to avoid contaminating the scaling parameters
with test-set statistics.

Results: RMSE = 115.18, MAE = 56.34, R2 = 0.236. The baseline_report.md
documents SEED = 42, the 80/20 split, preprocessing choices, and the
model's known limitation: Ridge's additive linear structure cannot capture
spatial interactions between coordinates and specific room types, which
are the dominant price drivers. This limitation statement directly motivated
the Task 04 model change.

**What it failed at:**

The `baseline_results.csv` only reports test-set metrics. There are no
train or validation scores. Without train metrics, it is not possible to
assess the bias-variance position of the model. Geron (2019, Ch.2) and
Prince (2023, Ch.8) both describe the train/test performance gap as the
primary diagnostic for overfitting: if training error is low but
generalisation error is high, the model has overfit. A Ridge model on
this dataset with R2 = 0.236 could be underfitting (high bias, low
variance) or fitting adequately and facing irreducible noise, and the
single-split test metric alone cannot distinguish between these. A
proper evaluation harness would report all three splits.

The CSV schema used (`metric_name`, `value`) does not match the group
README specification (`model_name`, `metric_name`, `metric_value`, `split`).
This inconsistency prevented direct cross-agent comparison in the results
table without manual reshaping.

**Iterations needed:**
2. First output reported only test metrics. Second prompt explicitly
requested train, validation, and test evaluation per split.

**The prompt that worked best:**
```
Build a Ridge Regression baseline on ingested.csv. Split 80/20 SEED=42.
Use TransformedTargetRegressor with log1p on the target.
Fit all preprocessing inside a Pipeline on train only -- never the full dataset.
Report RMSE, MAE, R2 on train, val, and test splits separately.
Save to outputs/baseline_results.csv with columns: metric_name, value.
Save model as outputs/model.pkl. Write baseline_report.md. SEED=42 throughout.
```

**How I verified the output:**
Loaded `model.pkl` and confirmed a fitted Pipeline object. Checked column
headers and numeric values in `baseline_results.csv`. Manually recomputed
RMSE = 115.18 on the test set to confirm it matched.

---

## Task 04: Improving Performance

**What the agent helped with:**

The model was upgraded from Ridge Regression to `HistGradientBoostingRegressor`
with `TargetEncoder` applied to the `neighbourhood` column. The `neighbourhood`
feature has 221 distinct values and was excluded from the baseline due to
cardinality, but it encodes hyper-local spatial pricing information that
a gradient-boosted tree can partition on. Geron (2019, Ch.2) notes that
geographic coordinates are among the most useful features in spatial
datasets because models can discover spatial clusters not visible in the
tabular feature space.

The critical methodological point is leakage handling in the target encoding.
A naive implementation of mean-target encoding computes neighbourhood mean
prices on the full training set, which contaminates the encoding with
information from the rows being trained on (target leakage). Sklearn's
`TargetEncoder` handles this by applying cross-validation smoothing during
`fit()`: each fold's encoding is computed on out-of-fold rows only, preventing
any single training row from informing its own encoding. Antigravity placed
the `TargetEncoder` inside the Pipeline `fit()` call rather than applying it
before the split, which is the correct pattern.

Results: RMSE improved from 115.18 to 106.07 (-7.91%), MAE from 56.34 to
50.59 (-10.21%), R2 from 0.236 to 0.352. A reduction of approximately $9
in average prediction error is practically significant for an Airbnb pricing
tool. R2 improved by 49% in relative terms. Both Codex and Claude also
improved on their baselines, so cross-agent comparison on this task requires
looking at the absolute RMSE values and the methods used, not just the delta.

**What it failed at:**

The `improvement_report.md` only documents the approach that worked. There
is no record of rejected approaches. For a benchmarking study, the absence
of failure documentation is a methodological gap: the report cannot answer
whether the improvement required one attempt or five, or whether alternative
approaches such as spatial clustering using latitude/longitude were tried and
abandoned. A single-strategy improvement report does not distinguish a well-
calibrated agent from one that happened to succeed on the first try.

The `improved_results.csv` uses columns `metric_name`, `baseline_value`,
`improved_value`, `delta_pct`, which is a different schema from
`baseline_results.csv`. The delta_pct column is useful but the schema
change means the two files cannot be joined for cross-task analysis without
reshaping.

**Iterations needed:**
1. Single prompt produced the improved model and all output files. No
leakage was detected on manual inspection of the Pipeline structure.

**The prompt that worked best:**
```
Improve on the Task 03 Ridge baseline. Use HistGradientBoostingRegressor.
Apply TargetEncoder to the neighbourhood column -- inside the Pipeline
to prevent leakage. Keep SEED=42. Show baseline vs improved metrics
side by side. Save improved_model.pkl and improvement_report.md explaining
what was tried, what worked, and confirming no leakage was introduced.
```

**How I verified the output:**
Confirmed `TargetEncoder` appeared inside the Pipeline `.fit()` call, not
before the split. Loaded `improved_model.pkl` and confirmed a fitted
Pipeline object. Verified delta values against manual computation from
both CSVs.

---

## Overall Reflection: Antigravity

**Strengths:**

Antigravity performed well on tasks that the SSRN human-AI task tensor
(2024) would classify as "verifiable applications": structured outputs
with clear correctness criteria, where the human can audit the outcome
without needing to reproduce the full generative process. When given
explicit output schemas and file names, Antigravity consistently placed
files in the correct directories and produced output that passed automated
scoring. Task 01 (5/5, 15 min) was completed faster than both Codex
(5/5, 25 min) and Claude (2/5, 20 min), and the score advantage over
Claude is directly traceable to Antigravity's documentation of imputation
rationale, which passed the manual check.

The Task 03 to Task 04 progression shows genuine cross-task continuity.
The choice of `HistGradientBoostingRegressor` with `TargetEncoder` in
Task 04 is not a generic improvement attempt: it responds specifically
to the Task 02 finding that categorical location features dominate price
prediction, and the Task 03 limitation note that Ridge cannot capture
spatial interactions. This chain of reasoning across tasks is not typical
of agents that treat each prompt independently.

**Weaknesses:**

Antigravity's primary failure mode is inconsistent output schemas across
tasks. `baseline_results.csv` and `improved_results.csv` use different
column structures. `schema_log.md` omits fields that were specified in
the group README. These are not one-off formatting errors; they suggest
the agent optimises for locally correct outputs rather than schema
compliance across the full pipeline. In a production ML system, this
would break automated downstream joins between task outputs.

The absolute path failure in Task 01 is a structural property of how
Antigravity integrates with VS Code: it resolves paths relative to the
currently open workspace window, not the repo root. Any team using
Antigravity across multiple machines needs an explicit relative path
constraint in every prompt that writes to disk.

The Task 04 improvement report documents only the successful strategy.
The absence of rejected alternatives means the benchmarking study cannot
use Antigravity's Task 04 log as evidence of how the agent behaves when
its first approach fails. Claude's Task 04 prompt log includes more
iteration detail, which produces richer comparative evidence even if the
final score is similar.

The evaluation harness gap in Task 03 is the most consequential weakness
for statistical validity. Reporting only test-set metrics, as Prince (2023,
Ch.8) notes, does not allow a reader to distinguish underfitting from an
appropriately regularised model facing irreducible noise. A benchmark
that compares tools on modelling quality should require all three splits.

**Verdict:**

Antigravity is a reliable accelerator for structured pipeline tasks where
the success criteria are defined upfront and the outputs are machine-checkable.
It is less suited to tasks that require an audit trail of the decision process
(Prince 2023, Table 3.4: "process explorations"), such as documenting why
certain approaches were rejected. The recommended workflow for teams using
Antigravity is: specify exact output schemas and filenames in the prompt,
include an explicit relative path constraint, require multi-split evaluation
in any modelling task, and treat the improvement report as a human-written
document rather than delegating it to the agent.
