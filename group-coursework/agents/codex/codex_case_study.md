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

## 3) Short Reflection
- Codex was strongest at fast pipeline assembly and documentation scaffolding.
- Most failures were execution-environment assumptions and path consistency during iterative refactors.
- Human verification was essential for runtime reliability and merge-safe naming discipline.
