# Agent Notes — Claude (claude.ai)

All observations are drawn from committed output files in
`agents/claude/task_0X/outputs/`, prompt logs in `task_0X_claude/prompt_log_claude.md`,
and cross-referenced against `results/scores.csv`.

---

## Task 01 — Data Ingestion

**What the agent helped with:**

Claude correctly identified all quality issues in the dataset: structural
missingness in `last_review` and `reviews_per_month` affecting the same 10,052
listings with no review history; `id`, `host_id`, and `host_name` columns with
no modelling value; `minimum_nights` outliers (values > 365 nights); and extreme
`price` values including zero-price listings. The schema log, missingness report,
and outlier flags were all produced without prompting for each file individually.
The final `ingested.csv` was confirmed at 48,895 rows after the path bug was fixed.

After the Iteration 2 fix, the agent generated a robust project-root finder:

```python
def _find_project_root() -> Path:
    for candidate in [Path.cwd()] + list(Path.cwd().parents):
        if (candidate / 'data' / 'raw').exists():
            return candidate
    raise FileNotFoundError(...)
```

This traverses parent directories until it finds the expected repo structure,
making the notebook runnable from any working directory without hardcoded paths.

**What it failed at:**

Iteration 1 produced `ingested.csv` with **0 rows**. The path
`../../data/raw/AB_NYC_2019.csv` resolved incorrectly because VS Code sets the
Jupyter kernel's working directory to the project root, not the notebook folder.
`pd.concat([])` returned an empty DataFrame with the correct column schema and
raised no error. The failure was completely silent — the notebook ran to
completion and printed "Loaded: 0 rows" without halting.

The `missingness_report.csv` listed counts and percentages but did not include
written justification for each imputation decision. The automated keyword check
passed (the word "strategy" appeared), but the manual check failed because there
was no per-column rationale explaining why each missing field was handled the
way it was. Score: 2/5.

**Iterations needed:**
2. Iteration 1: 0-row silent failure from path resolution bug.
Iteration 2: Fixed with pathlib resolved relative to the notebook file;
added a FileNotFoundError guard. Output correct on second attempt.

**The prompt that worked best:**
```
The notebook produced 0 rows in ingested.csv. The path ../../data/raw/
resolves incorrectly in VS Code — the kernel runs from the project root,
not the notebook folder. Fix the path using pathlib resolved relative to
the notebook file itself, or use an explicit path from the repo root.
Also add a guard: if the file is not found, raise a FileNotFoundError
immediately rather than silently loading 0 rows.
Re-run and confirm the row count is 48,895.
```

**How I verified the output:**
Ran `evaluate.py`. Checked `ingested.csv` file size (should be ~60 MB, not ~10 KB).
Manually confirmed `df.shape[0] == 48895`. Checked that `missingness_report.csv`
contained decision notes for each missing feature column.

---

## Task 02 — EDA and Insight Generation

**What the agent helped with:**

Claude produced 9 plots with a markdown interpretation cell after each one:
price distribution (raw and log1p), correlation heatmap, median price by borough,
median price by room type, geographic scatter on latitude/longitude, neighbourhood
price rankings, pairplot of numeric features, and categorical counts. Every plot
had a title, labelled axes, and a written interpretation — all requirements were
met without prompting for each individually.

The `eda_summary.md` went beyond restating what the plots showed. It included a
"Feature Engineering Recommendations for Task 04" section — written at Task 02 —
that correctly anticipated neighbourhood target encoding, geo-clustering,
interaction terms, and log transforms on skewed numerics. All four of those
recommendations were implemented in Task 04. The reasoning was carried forward,
not just the outputs.

Data quality decisions were conservative and justified: `price` capped at the
99th percentile (not an arbitrary round number), `minimum_nights` clipped at 30.

**What it failed at:**

Nothing that affected the score. Task 02 was the cleanest run: 5/5 in a
single iteration. The only minor gap was that the correlation heatmap did not
quote Pearson r values in the interpretation cell — relationships were described
as "weak" or "strong" without grounding the claim in the numeric coefficient
visible in the plot.

**Iterations needed:**
1. Single prompt produced all required outputs.

**The prompt that worked best:**
```
Your job is Task 02: EDA and Insight Generation.
Your input: ../task_01/outputs/ingested.csv

[5-step specification: target variable, features, relationships,
data quality decisions, EDA summary]

CONSTRAINTS:
- Do NOT create a train/test split in this notebook
- Every plot must have a title, labelled axes, and a markdown interpretation cell
- Save all outputs to outputs/ using relative paths only
```

**How I verified the output:**
Counted PNG files in `outputs/` (9 found, requirement ≥3). Opened `eda_summary.md`
and confirmed modelling recommendations beyond plot descriptions. Confirmed no
`train_test_split` call anywhere in the notebook. Checked `eda_cleaned.csv`
shape against `ingested.csv`.

---

## Task 03 — Baseline Model

**What the agent helped with:**

The baseline is Ridge Regression trained on `log1p(price)` as the target, using
a scikit-learn `Pipeline` with `ColumnTransformer` (OneHotEncoder on `room_type`
and `neighbourhood_group`, StandardScaler on 7 numeric features). The notebook
reads the EDA summary before writing any modelling code and explicitly justifies
Ridge over OLS (multicollinearity after one-hot encoding) and the log transform
over raw price (right skew).

Claude saved `split_meta.pkl` alongside the model — a dictionary containing
train and test indices, SEED, feature lists, and split proportions. This allowed
Task 04 to reconstruct the exact same split without re-splitting, guaranteeing
both tasks evaluated on identical held-out data. No other agent saved this
reproducibility artefact.

Results: RMSE = 83.32, MAE = 47.95, R² = 0.549 (log scale).
Train RMSE = 83.65 — nearly identical to test, confirming no overfitting.

**What it failed at:**

Output files were saved with non-standard names: `model_selection_reasoning.md`
instead of `baseline_report.md`, and `baseline_pipeline.pkl` instead of `model.pkl`.
The automated check for `baseline_report.md` failed. Score: 4/5.

This is a recurring pattern for Claude on structured-output tasks: the content
is correct but the filename does not match the specification. The agent defaults
to names it considers descriptive rather than checking the exact string in the
prompt. An explicit naming constraint ("save as outputs/model.pkl — no other
filename") would prevent this.

Iteration 2 added train-set metrics to `baseline_results.csv`. The first output
contained only a test row.

**Iterations needed:**
2. Iteration 1: train metrics missing from results CSV.
Iteration 2: train row added. File naming was not corrected, as the Task 04
notebook already referenced `baseline_pipeline.pkl` and changing it would
have broken that dependency.

**The prompt that worked best:**
```
Your job is Task 03: Baseline Model Training and Evaluation Harness.
SEED = 42

[6-step specification: model reasoning, split, pipeline, train, evaluate, save]

CONSTRAINTS:
- SEED=42 must be used for the split and the model
- Preprocessing must be fitted on train data only — never on the full dataset
- Do NOT tune hyperparameters
- Document every decision in a markdown cell
- Save all outputs to outputs/ using relative paths only
```

**How I verified the output:**
Loaded `baseline_pipeline.pkl` and confirmed a fitted sklearn Pipeline object.
Checked `baseline_results.csv` for both train and test rows. Manually recomputed
RMSE = 83.32 on the test set. Verified `pipeline.fit(X_train, y_train)` was the
only fit call in the notebook.

---

## Task 04 — Improving Performance

**What the agent helped with:**

Task 04 is the most methodologically transparent output of the three agents.
The notebook opens with a written diagnosis of the baseline before touching any
code (four weaknesses: heteroscedasticity, lost neighbourhood granularity, no
interaction terms, skewed numerics fed raw). Improvement strategies are then
ranked by expected impact with stated risks before any implementation. This
structured approach — diagnose, reason, implement, evaluate — is documented in
`improvement_reasoning.md` and makes the decision trail fully auditable.

Two strategies were implemented and compared against the same baseline:
- **Strategy A (Ridge + Feature Engineering):** RMSE 80.09
- **Strategy B (Random Forest + Feature Engineering):** RMSE 74.87, R² = 0.485

Feature engineering included neighbourhood target encoding (mean log1p(price)
per neighbourhood computed on `df_train` only), geo-clustering with k-means
k=20 fitted on `df_train[['latitude','longitude']]` only, log1p transforms on
skewed numerics, a `room_type × neighbourhood_group` interaction, and binary
flags. All transformations were computed or fitted on training data exclusively.

**What it failed at:**

**Iteration 2 — LightGBM validation contamination:**
The first draft passed the comparison validation set directly to LightGBM's
early stopping:

```python
# WRONG — X_val used for both early stopping and final comparison
lgbm.fit(X_train, y_train, eval_set=[(X_val, y_val)])
```

LightGBM uses `eval_set` to decide when to stop adding trees. When that set
is the same one used for final metric comparison, LightGBM has seen validation
labels during training while Ridge and RF had not — an unfair advantage that
inflated LightGBM's apparent performance. No error is raised; the results look
plausible. It only becomes visible when reading the training loop.

Fix: create an internal 90/10 split from `X_train` for early stopping only.
After the fix, Random Forest still outperformed LightGBM (RMSE 74.87 vs ~77).

**Iteration 3 — hardcoded feature importance plot:**
The feature importance section was hardcoded to select LightGBM importances
regardless of which model actually scored best. Fixed to derive importances
from the model with the lowest RMSE dynamically.

Both failures required human review to detect — neither raised an error.

**Iterations needed:**
3. Iteration 1: full implementation with leakage bug.
Iteration 2: LightGBM early stopping contamination fixed.
Iteration 3: hardcoded importance plot corrected.

**The prompt that worked best:**
```
Your job is Task 04: Improving Performance.

[4-step specification: diagnose, reason, implement ≥2 strategies, evaluate]

CONSTRAINTS:
- The test set must not influence any training, tuning, or feature decisions
- Any feature derived from the target variable must be computed on train only
- You MUST show the baseline result alongside your improved result
- Do NOT use any data source other than eda_cleaned.csv
- Document every decision in a markdown cell
- Save all outputs to outputs/ using relative paths only
```

**How I verified the output:**
Confirmed `df_train.groupby(...)` and `kmeans.fit(df_train[...])` — train only.
Ran `leakage_check.py batch` (5/5). Loaded `improved_pipeline_rf.pkl`.
Manually checked the LightGBM training block to confirm the fix used an
internal split, not `X_val`.

---

## Overall Reflection — Claude

**Strengths:**

Claude performs best on tasks requiring a documented reasoning trail. The
notebooks include markdown cells before every major code block explaining
the decision — why this model, why this split ratio, why this feature. In
a benchmarking study where the reasoning matters as much as the metric,
this documentation is directly usable in a written report without further
editing.

The `split_meta.pkl` pattern is the clearest example of cross-task
continuity. Rather than re-splitting in Task 04 and assuming the same
indices would emerge from `random_state=42`, Claude saved the exact indices
and reloaded them. This is a correctness requirement for comparing a
baseline and an improved model: if the test indices differ, even by a
single row, the metric comparison is not valid.

Claude is also the only agent that documented a failed approach: the
LightGBM contamination and the hardcoded importance plot are both recorded
in the prompt log as bugs found and fixed. This failure documentation is
more valuable for a comparative study than a clean result with no revision
history.

**Weaknesses:**

Output schema compliance is the consistent failure mode. Across Tasks 01,
03, and 04, Claude produced files with names and structures that were
correct in content but did not match the exact specification. This is
preventable: when the CONSTRAINTS section lists exact filenames, Claude
follows them. When it does not, the agent uses names it considers
descriptive, which fail keyword-matching automated checks.

The Task 01 silent failure (0 rows, no error) is a structural risk for any
path-dependent task. A defensive `assert len(df) > 0` after every data load
should be standard in any prompt that reads from disk.

The LightGBM eval_set contamination was not caught by the automated leakage
checker. `leakage_check.py` verifies cell ordering and Pipeline usage but
does not inspect training loop arguments. Validation-set contamination in
hyperparameter-search loops remains a gap that requires human review.

**Would I use it again for DS work?**

Yes, with two adjustments: (1) always include explicit output filenames in
the CONSTRAINTS section, and (2) add a row-count assertion after every data
load. With those guards, Claude is reliable across a full four-task pipeline.
The reasoning documentation it produces reduces the report-writing burden
significantly — the markdown cells in the notebooks translate directly into
report prose without requiring a separate write-up pass.
