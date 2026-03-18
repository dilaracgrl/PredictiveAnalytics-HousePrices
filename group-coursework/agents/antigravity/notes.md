# Agent Notes: Antigravity

All observations are drawn from committed output files in
agents/antigravity/task_0X/outputs/ and cross-referenced against
results/scores.csv. Where comparisons to Claude and Codex are made,
they reference the same committed outputs in their respective agent folders.

---

## Task 01: Data Ingestion

**What the agent helped with:**

Antigravity correctly handled the structural missingness in the dataset.
The 20.56% missingness in `last_review` and `reviews_per_month` affects
the same 10,052 listings: those with no review history at all. Rather than
dropping those rows, which would have removed roughly one in five listings
and systematically excluded newer or less popular properties from the
training distribution, the agent applied sentinel imputation. `last_review`
nulls were filled with "No review" and `reviews_per_month` nulls with 0.0.
The distinction matters: a missing review frequency is not the same as
an unknown one, and preserving that signal avoids fabricating data where
none exists.

The agent also produced `outlier_flags.txt` without being asked, flagging
`minimum_nights > 365`, `price <= 0`, and `price > 5000`, but did not
remove those rows. This is correct: any filtering based on the target
variable `price` before exploratory analysis constitutes a form of data
snooping, where the analyst's knowledge of the test distribution
influences modelling decisions. Deferring row removal to post-EDA
stages keeps the ingestion step clean of that contamination.

Compared to Claude (Task 01 score: 2/5, 20 minutes), Antigravity scored
5/5 in 15 minutes. The score gap is traceable to a single failure in
Claude's output: the `missingness_report.md` contained the word "strategy"
and therefore passed the automated keyword check, but did not include
written justification for each imputation decision. Antigravity's report
addressed all four missing columns with stated rationale per column, which
passed the manual check. Codex also scored 5/5 but took 25 minutes.
Antigravity was the fastest to a full score on this task.

**What it failed at:**

The `schema_log.md` covered column names and dtypes but omitted value
ranges and cardinality counts. A complete schema audit at ingestion should
quantify the min and max of numeric columns and the count of distinct
categories for categorical ones. Without those values in Task 01, downstream
tasks had to rediscover the outlier ranges for `price` and `minimum_nights`
independently in Task 02.

The first prompt output used a hardcoded absolute path
(`C:\Users\Caroline Kelly\...`). This is a structural limitation of
IDE-embedded agents: Antigravity resolves paths relative to the VS Code
workspace window rather than the repository root. It is not a one-off
error but a predictable failure mode for any team member opening the
project from a different machine. The fix required a second prompt with
an explicit relative path constraint, documented in `task_01/prompt_log.md`.

**Iterations needed:**
2. First prompt produced an absolute path. Second prompt added the
relative path constraint. Output was correct on the second attempt.

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
restating what the plots showed. Antigravity identified that `price` is
heavily right-skewed and recommended `log1p` transformation before fitting
any regression model. This was carried forward into Task 03 via
`TransformedTargetRegressor`, making Task 02 and Task 03 methodologically
consistent. An agent that does not carry EDA findings into model design
produces disconnected outputs; this one did not.

Antigravity identified that continuous numeric features (`minimum_nights`,
`availability_365`) have weak linear correlation with price, while
categorical features (`room_type`, `neighbourhood_group`) are the primary
structural drivers. That prediction proved accurate: the Ridge baseline in
Task 03 achieved R2 = 0.236, consistent with a dataset where the dominant
signal is categorical and a linear model without high-cardinality neighbourhood
encoding will underfit.

Collinearity between `reviews_per_month` and `number_of_reviews` was flagged,
informing feature selection in subsequent tasks.

**What it failed at:**

The `eda_cleaned.csv` output in the Task 02 folder indicates some preprocessing
was applied during EDA. It was not immediately clear from the notebook
structure whether this happened before or after the train/test split. Any
summary statistic computed on the full dataset before the split, even one
as simple as a `value_counts()` call, allows test-set information to
influence analytical decisions. That is data snooping, and it biases any
downstream interpretation of model performance. Manual inspection of the
notebook cell order was needed to confirm the split came first.

The EDA insights described correlations in qualitative terms ("remarkably
weak") without quoting the actual Pearson r values visible in the committed
heatmap plot. Quantitative claims should be grounded in the numbers, not
just the visual impression.

**Iterations needed:**
1. Single prompt produced all required output files. Manual review was
needed to confirm the leakage boundary.

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
Confirmed three `.png` files were present. Traced the notebook cell order
to confirm the split preceded the first `value_counts()` call.

---

## Task 03: Baseline Model

**What the agent helped with:**

The baseline uses Ridge Regression wrapped in `TransformedTargetRegressor`
with `log1p` on the target. This responds directly to the Task 02 finding
about price skewness. The full sklearn `Pipeline` encapsulates
`ColumnTransformer` (StandardScaler on numeric columns, OneHotEncoder on
`neighbourhood_group` and `room_type`) with the estimator, so the scaler
and encoder are fitted on X_train only and `.transform()` is called on
the test set separately. This is the correct pattern: fitting transformers
on the full dataset before the split leaks test-set statistics into the
training distribution and produces an overly optimistic evaluation.

Results: RMSE = 115.18, MAE = 56.34, R2 = 0.236. The `baseline_report.md`
documents SEED = 42, the 80/20 split, preprocessing choices, and a
limitation statement: Ridge's additive linear structure cannot capture
spatial interactions between coordinates and specific room types. That
limitation statement directly motivated the Task 04 model choice.

**What it failed at:**

The `baseline_results.csv` only reports test-set metrics. There are no
train or validation scores. Without train metrics, it is not possible to
diagnose the bias-variance position of the model. A train R2 near 0.236
would indicate the model is underfitting, while a train R2 substantially
higher than 0.236 would indicate it is overfitting the training data and
the test generalisation is limited by variance rather than bias. A single
test metric cannot distinguish these two situations, and the correct
response to each is different: underfitting calls for a more expressive
model, overfitting calls for more regularisation or more data.

A second validation set is also needed for honest hyperparameter selection.
If the hyperparameter that minimises test error is selected by repeatedly
evaluating against the test set, the reported test performance will be
optimistic, because the model has been implicitly tuned to that specific
held-out sample. Task 03 did not tune hyperparameters so this did not
cause an error here, but the harness should be designed correctly from
the start.

The CSV schema (`metric_name`, `value`) does not match the group README
specification (`model_name`, `metric_name`, `metric_value`, `split`).
This prevented direct cross-agent comparison without manual reshaping.

**Iterations needed:**
2. First output reported only test metrics. Second prompt requested
train, validation, and test evaluation per split explicitly.

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
headers and values in `baseline_results.csv`. Manually recomputed
RMSE = 115.18 on the test set to confirm it matched.

---

## Task 04: Improving Performance

**What the agent helped with:**

The model was upgraded from Ridge Regression to `HistGradientBoostingRegressor`
with `TargetEncoder` applied to the `neighbourhood` column. The `neighbourhood`
feature has 221 distinct values and was excluded from the baseline because
one-hot encoding 221 categories would produce a very sparse matrix and
introduce multicollinearity problems with Ridge. Gradient-boosted trees
handle high-cardinality categoricals more naturally by learning splits on
the encoded values directly. Geographic granularity is also where most of
the unexplained variance in Airbnb pricing sits: a listing in Williamsburg
is priced differently from one in the Financial District even if all other
features are identical.

The critical methodological point is the leakage handling in target
encoding. A naive implementation computes the mean price per neighbourhood
on the full training set, then uses those means as the encoded feature.
This leaks target information into the training features: each training
row is encoded using a mean that includes its own target value. Sklearn's
`TargetEncoder` avoids this by using cross-validation smoothing during
`fit()`, computing each fold's encoding from out-of-fold rows only.
Antigravity placed the `TargetEncoder` inside the Pipeline `.fit()` call
rather than applying it before the split, which is the correct position.

Results: RMSE fell from 115.18 to 106.07 (-7.91%), MAE from 56.34 to
50.59 (-10.21%), R2 from 0.236 to 0.352. A reduction of roughly $9 in
average absolute prediction error is practically significant for a pricing
tool. The R2 improvement of 49% in relative terms reflects the model
now capturing neighbourhood-level price clustering that Ridge could not.

**What it failed at:**

The `improvement_report.md` only documents the approach that worked.
There is no record of rejected alternatives. The report cannot answer
whether spatial clustering using latitude and longitude was tried and
discarded, whether log-transforming the target alone (without changing
the model) was tested first, or how many iterations were needed to reach
the final configuration. For a benchmarking study, the absence of failure
documentation is a methodological gap: a single-strategy report does not
distinguish a well-calibrated agent from one that succeeded by chance on
its first attempt.

The `improved_results.csv` uses columns `metric_name`, `baseline_value`,
`improved_value`, `delta_pct`. This differs from `baseline_results.csv`
and prevents direct cross-task joins without reshaping.

**Iterations needed:**
1. Single prompt produced the improved model and all output files.
No leakage was detected on manual inspection.

**The prompt that worked best:**
```
Improve on the Task 03 Ridge baseline. Use HistGradientBoostingRegressor.
Apply TargetEncoder to the neighbourhood column -- inside the Pipeline
to prevent leakage. Keep SEED=42. Show baseline vs improved metrics
side by side. Save improved_model.pkl and improvement_report.md explaining
what was tried, what worked, and confirming no leakage was introduced.
```

**How I verified the output:**
Confirmed `TargetEncoder` appeared inside the Pipeline `.fit()` call,
not before the split. Loaded `improved_model.pkl` and confirmed a fitted
Pipeline object. Verified delta values against manual computation from
both CSVs.

---

## Overall Reflection: Antigravity

**Strengths:**

Antigravity performed best on tasks with clear, machine-checkable output
criteria. Task 01 (5/5, 15 minutes) was completed faster than both Codex
(5/5, 25 minutes) and Claude (2/5, 20 minutes), and the score difference
over Claude on that task is directly traceable to Antigravity's
documentation of imputation rationale rather than any difference in the
code produced.

The Task 03 to Task 04 progression shows genuine cross-task continuity.
The choice of `HistGradientBoostingRegressor` with `TargetEncoder` in
Task 04 is not a generic upgrade: it responds to the specific Task 02
finding that categorical location features dominate price prediction
and the Task 03 limitation note that Ridge cannot capture spatial
interactions. This kind of reasoning across tasks is not typical of
agents that treat each prompt as an isolated request.

The agent also produced supplementary outputs that were not required
(`outlier_flags.txt`, `eda_cleaned.csv`, `model_selection_reasoning.md`).
These did not affect the automated score but added analytical transparency
to the pipeline.

**Weaknesses:**

The primary failure mode across all four tasks is inconsistent output
schemas. `baseline_results.csv` and `improved_results.csv` use different
column structures. `schema_log.md` omits fields that were in the group
README. These are not isolated formatting errors: they indicate the agent
optimises for locally plausible outputs rather than checking schema
compliance across the full pipeline. In a production setting, inconsistent
schemas break automated downstream joins and require human correction
before any cross-task analysis can run.

The absolute path failure in Task 01 is a structural property of how
Antigravity integrates with VS Code. It resolves paths relative to
the currently open workspace window, not the repo root. Any team using
Antigravity on multiple machines needs an explicit relative path
constraint in every prompt that writes to disk.

The evaluation harness in Task 03 reported only test-set metrics. Without
train and validation scores, a reader cannot determine whether the model
is underfitting, overfitting, or sitting at an appropriate bias-variance
balance. This gap limits the diagnostic value of the baseline for any
subsequent improvement task.

The Task 04 improvement report records only the successful strategy.
Claude's prompt logs include more iteration detail, which generates
richer evidence for the comparative analysis even where the final
metric is similar.

**Verdict:**

Antigravity is well suited to structured tasks where the success criteria
are defined upfront and the output is machine-checkable. It is less suited
to tasks requiring an audit trail of the reasoning process, including
documentation of rejected approaches and per-split evaluation.

The recommended workflow for teams using Antigravity is: specify exact
output schemas and filenames in the prompt, include a relative path
constraint in every prompt that writes to disk, require multi-split
evaluation in any modelling task, and treat the improvement report as
a document requiring human authorship rather than agent delegation.
Antigravity accelerates the code-writing step but does not replace
the human judgment needed to verify leakage, confirm schema compliance,
or document the full decision trail.
