# Agent Notes - Codex

> Filled from actual Task 01-04 execution in the Codex workspace.

---

## Task 01 - Data Ingestion

**What the agent helped with:**
- Built a complete ingestion pipeline from raw CSV to cleaned output.
- Produced schema and missingness artifacts and documented cleaning decisions.
- Added evaluator-compatible files and notebook versions.

**What it failed at:**
- First run used a wrong relative input path (`../../data/raw/...`) from task folder and failed with `FileNotFoundError`.
- Needed a correction to `../../../data/raw/AB_NYC_2019.csv`.

**Iterations needed:**
- 2 main iterations (initial run + path fix), plus notebook conversion.

**The prompt that worked best:**
```text
Task 01: load ../../data/raw/AB_NYC_2019.csv, inspect schema, create missingness + outlier reports,
apply justified cleaning decisions, and save ingested.csv and reports to outputs using relative paths and SEED=42.
Do not split data and do not transform target price.
```

**How I verified the output:**
- Ran `tasks/task_01_data_ingestion/evaluate.py` on Codex task folder.
- Confirmed score `5/5` and row appended in `results/scores.csv`.
- Confirmed output files exist in the task output directory.

---

## Task 02 - EDA

**What the agent helped with:**
- Generated a full EDA pack with multiple saved plots and written summary.
- Created `eda_cleaned.csv` and `eda_summary.md` for downstream tasks.
- Converted workflow into `.ipynb` while keeping outputs organized.

**What it failed at:**
- Assumed `seaborn` was installed (module import failed).
- Matplotlib default backend required GUI/Tk and failed in this environment.

**Iterations needed:**
- 3 iterations (initial script, dependency/backend fixes, notebook conversion).

**The prompt that worked best:**
```text
Task 02: use only ../task_01/outputs/ingested.csv, create target/feature/relationship plots with
titles and labels, add markdown interpretations, create eda_cleaned.csv and eda_summary.md, and
save all outputs with relative paths and SEED=42 (no train/test split).
```

**How I verified the output:**
- Checked all required files in task output folder (plots + summary + cleaned dataset).
- Manually reviewed summary consistency with plotted patterns.

---

## Task 03 - Baseline Model

**What the agent helped with:**
- Built a baseline regression pipeline with train-only preprocessing.
- Reported RMSE, MAE, and R2.
- Saved model artifacts and diagnostic plots for Task 04.

**What it failed at:**
- Non-ASCII character (`R2` formatting as special symbol) caused script parse issue and needed cleanup.
- Some environment timeouts required reruns with adjusted command timeout.

**Iterations needed:**
- 2-3 iterations (script draft, encoding fix, notebook conversion).

**The prompt that worked best:**
```text
Task 03: read ../task_02/outputs/eda_cleaned.csv, reason about baseline model choice first,
split 80/20 with SEED=42, fit preprocessing on train only, train a simple baseline, report RMSE/MAE/R2,
save diagnostics and model artifacts to outputs, and document leakage controls.
```

**How I verified the output:**
- Confirmed `baseline_results.csv`, `.pkl` files, diagnostics, and reasoning docs exist.
- Checked metrics format and leakage statement in report.

---

## Task 04 - Improving Performance

**What the agent helped with:**
- Diagnosed weak baseline and implemented two improvement strategies.
- Produced honest baseline vs improved comparison and selected best strategy.
- Saved `improved_results.csv`, `improved_model.pkl`, comparison chart, and reasoning report.

**What it failed at:**
- Initial CV/tuning approach was too heavy for environment constraints (timeouts/parallel permission issues).
- Needed model simplification and single-process settings to finish reliably.

**Iterations needed:**
- 4+ iterations (initial search approach, parallelism fixes, simplification, notebook conversion).

**The prompt that worked best:**
```text
Task 04: start from baseline outputs and EDA summary, diagnose baseline first, rank improvement
strategies with risks, implement at least two non-leaky improvements, compare using same metrics
(RMSE/MAE/R2), save improved_results.csv + charts + improved model + reasoning to outputs.
```

**How I verified the output:**
- Checked `improved_results.csv` includes baseline and improved values side by side.
- Confirmed improved metrics over baseline and presence of required artifacts.

---

## Overall Reflection - Codex

**Strengths of this tool:**
- Very strong at turning structured prompts into full runnable pipelines quickly.
- Good persistence in debugging (path issues, missing packages, runtime constraints).
- Produces usable documentation artifacts alongside code and outputs.

**Weaknesses:**
- Sometimes assumes environment capabilities (libraries/backend/parallelism) that are not available.
- Can require multiple passes when runtime constraints are strict.
- Large refactors (renaming paths/folders) can introduce consistency clean-up overhead.

**Would I use it again for DS work?**
- Yes, conditionally. Best for fast prototyping, pipeline assembly, and reproducible task execution,
  with human checks for leakage, environment assumptions, and final reporting quality.
