# Codex Mini Case Study (Step A)

## 1) Where Codex Helped

### Case 1: Task 01 Data Ingestion and Reproducibility Setup
- What Codex did well:
  - Built a full ingestion workflow from raw CSV to cleaned output.
  - Produced required artifacts (`ingested.csv`, schema/missingness reports, outlier flags).
  - Enforced reproducibility rules (`SEED = 42`, relative paths, no target transformation in Task 01).
- Why this helped:
  - Reduced setup/debug time and gave us a clean handoff into Task 02.
- Receipt:
  - Files in `agents/codex/task_01_codex/output_01_codex/`.
- Verification/Fix performed by us:
  - Ran evaluator and checked score row append in `results/scores.csv`.

### Case 2: Task 04 Baseline Improvement and Comparison Framing
- What Codex did well:
  - Implemented two improvement strategies and compared them against baseline using the same metrics.
  - Produced side-by-side comparison outputs and improvement reasoning.
- Why this helped:
  - Gave a clear, evidence-based performance story for report writing.
- Receipt:
  - `agents/codex/task_04_codex/output_04_codex/improved_results.csv`
  - `agents/codex/task_04_codex/output_04_codex/strategy_comparison.csv`
  - `agents/codex/task_04_codex/output_04_codex/improvement_reasoning.md`
- Verification/Fix performed by us:
  - Confirmed metrics improved over baseline and outputs were in correct folders.

## 2) Where Codex Failed (or Needed Intervention)

### Case 1: Environment Assumptions Broke Execution
- What failed:
  - Initial EDA/modeling attempts assumed optional packages/backends (e.g., `seaborn`, GUI matplotlib backend, multiprocessing behavior) that were not available in the runtime.
- Impact:
  - Script runs failed before output generation.
- Receipt:
  - Terminal errors encountered during run steps (module import/backend/permission errors).
- What we did to verify/fix:
  - Switched to `matplotlib` with `Agg` backend.
  - Removed dependency on unavailable plotting libraries.
  - Re-ran and verified output files were generated.

### Case 2: Path and Naming Drift During Refactor
- What failed:
  - After renaming task/output folders to include `codex`, several references still pointed to old paths (`outputs`, `task_0X`).
- Impact:
  - Risk of broken notebook/script references and merge confusion.
- Receipt:
  - Path strings in notebooks/logs needed updates.
- What we did to verify/fix:
  - Updated references to `task_0X_codex` and `output_0X_codex`.
  - Rechecked prompt logs and output paths after rename.

### Case 3: Negative R2 on Baseline Model Model Worse Than the Mean Predictor
- What failed:
  - Task 03 baseline produced RMSE = 150.58, MAE = 106.23, and R2 = -0.625. A negative R2 means the model performed worse than simply predicting the mean price for every listing. The code ran without errors and the results CSV looked like valid output.
- Impact:
  - A pipeline that completes successfully but produces a model worse than the mean predictor would have been submitted as a valid baseline with no automatic warning. Cross-referencing against Antigravity (R2 = 0.236) and Claude (R2 = 0.362) on the same dataset was the only way to identify the failure.
- Receipt:
  - `agents/codex/task_03_codex/output_03_codex/baseline_results.csv` shows R2 = -0.625. `agents/codex/task_04_codex/output_04_codex/improved_results.csv` shows the corrected result.
- What we did to verify/fix:
  - Root cause was the absence of a log transform on the `price` target. The price distribution is heavily right-skewed and extreme values dominated the squared error loss. Antigravity and Claude both applied `log1p` transforms to the target and both achieved positive R2 on the same data.
  - Task 04 switched to Random Forest, which is more robust to skewed targets without an explicit transform. RMSE improved from 150.58 to 86.53 and R2 from -0.625 to 0.463 -- the largest absolute improvement of any agent across all four tasks.
  
## 3) Short Reflection
- Codex was strongest at fast pipeline assembly and documentation scaffolding.
- Most failures were execution-environment assumptions and path consistency during iterative refactors.
- Human verification was essential for runtime reliability and merge-safe naming discipline.
