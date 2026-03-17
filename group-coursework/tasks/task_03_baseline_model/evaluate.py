"""
evaluate.py - Task 03: Baseline Model
Shared scoring script. All agents run their outputs through this file.

Usage:
    python tasks/task_03_baseline_model/evaluate.py \
        --agent agents/antigravity/task_03/ \
        --name caroline --tool "Antigravity" \
        --time 30 --notes "ridge regression" --failure "none"

    # For agents with renamed output folders:
    python tasks/task_03_baseline_model/evaluate.py \
        --agent agents/claude/task_03_claude/ \
        --outputs outputs_claude \
        --name dilara --tool "Claude (claude.ai)" \
        --time 35 --notes "..." --failure "..."
"""

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd

SCORES_CSV = Path("results/scores.csv")
TASK_ID = "task_03_baseline_model"
MAX_SCORE = 5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_outputs(agent_dir: Path, outputs_name: str) -> Path:
    direct = agent_dir / outputs_name
    if direct.exists():
        return direct
    for sub in agent_dir.iterdir():
        candidate = sub / outputs_name
        if candidate.exists():
            return candidate
    return direct


# ---------------------------------------------------------------------------
# Automated checks
# ---------------------------------------------------------------------------

def check_baseline_results_csv(outputs_dir: Path) -> tuple[bool, str]:
    f = outputs_dir / "baseline_results.csv"
    if not f.exists():
        return False, "FAIL - baseline_results.csv not found in outputs folder"
    try:
        df = pd.read_csv(f)
    except Exception as e:
        return False, f"FAIL - could not read baseline_results.csv: {e}"
    if len(df) == 0:
        return False, "FAIL - baseline_results.csv is empty"
    if df.isnull().sum().sum() > 0:
        nulls = df.isnull().sum()[df.isnull().sum() > 0].to_dict()
        return False, f"FAIL - baseline_results.csv contains null values: {nulls}"
    return True, f"PASS - baseline_results.csv present with {len(df)} row(s)"


def check_two_metrics(outputs_dir: Path) -> tuple[bool, str]:
    f = outputs_dir / "baseline_results.csv"
    if not f.exists():
        return False, "SKIP - baseline_results.csv not found"
    try:
        df = pd.read_csv(f)
    except Exception as e:
        return False, f"FAIL - could not read file: {e}"
    # Find metric column
    metric_col = None
    for col in ["metric_name", "metric"]:
        if col in df.columns:
            metric_col = col
            break
    if metric_col is None:
        return False, (f"FAIL - no metric_name column in baseline_results.csv. "
                       f"Found columns: {list(df.columns)}")
    n_metrics = df[metric_col].nunique()
    if n_metrics >= 2:
        metrics = df[metric_col].unique().tolist()
        return True, f"PASS - {n_metrics} distinct metric(s): {metrics}"
    return False, (f"FAIL - only {n_metrics} metric in baseline_results.csv. "
                   "Rubric requires at least 2 (e.g. RMSE + R2, or accuracy + F1).")


def check_model_file(outputs_dir: Path) -> tuple[bool, str]:
    # Accept any .pkl file as a saved model
    pkl_files = list(outputs_dir.glob("*.pkl"))
    if pkl_files:
        return True, f"PASS - model file present: {[f.name for f in pkl_files]}"
    return False, "FAIL - no .pkl model file found in outputs folder"


def check_baseline_report(outputs_dir: Path) -> tuple[bool, str]:
    f = outputs_dir / "baseline_report.md"
    if not f.exists():
        return False, "FAIL - baseline_report.md not found in outputs folder"
    content = f.read_text()
    content_lower = content.lower()

    # SEED=42 must appear explicitly - not just the number 42 in a results table
    has_seed = ("seed" in content_lower and "42" in content)
    # Split documentation: must mention specific proportions or sizes
    has_split = any(w in content_lower for w in
                    ["80/20", "80:20", "0.2", "0.8", "train_test_split",
                     "80%", "20%", "split"])
    # Preprocessing: must mention at least one preprocessing step
    has_preprocessing = any(w in content_lower for w in
                            ["scaler", "encoder", "pipeline", "standardscaler",
                             "onehotencoder", "imputer", "preprocessing"])
    failures = []
    if not has_seed:
        failures.append("SEED=42 not explicitly documented (number 42 alone is not sufficient)")
    if not has_split:
        failures.append("split proportions not documented")
    if not has_preprocessing:
        failures.append("no preprocessing steps described")
    if failures:
        return False, f"FAIL - baseline_report.md: {'; '.join(failures)}"
    return True, "PASS - baseline_report.md documents seed, split, and preprocessing"


# ---------------------------------------------------------------------------
# Manual checks
# ---------------------------------------------------------------------------

def manual_check_no_leakage(agent_dir: Path) -> tuple[bool, str]:
    print("\n[MANUAL CHECK 1 of 2] Open the Task 03 notebook.")
    print("Question: Are ALL scalers, encoders, and imputers fitted on")
    print("          training data only, with .transform() applied to val/test?")
    print("          (Check: no fit_transform() called on val or test data)")
    answer = input("Enter y/n: ").strip().lower()
    if answer == "y":
        return True, "PASS (manual) - preprocessing fitted on train only"
    return False, "FAIL (manual) - leakage: scaler or encoder fitted on val/test or full dataset"


def manual_check_seed_in_code(agent_dir: Path) -> tuple[bool, str]:
    print("\n[MANUAL CHECK 2 of 2] Open the Task 03 notebook.")
    print("Question: Does SEED=42 (or random_state=42) appear in the code cells")
    print("          controlling the train/test split and model instantiation?")
    answer = input("Enter y/n: ").strip().lower()
    if answer == "y":
        return True, "PASS (manual) - SEED=42 present in code"
    return False, "FAIL (manual) - SEED=42 missing from split or model code"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def run_evaluation(agent_dir: Path, outputs_name: str) -> tuple[int, list[str]]:
    outputs_dir = find_outputs(agent_dir, outputs_name)
    results = []
    score = 0

    for check_fn in [check_baseline_results_csv, check_two_metrics,
                     check_model_file, check_baseline_report]:
        ok, msg = check_fn(outputs_dir)
        results.append(msg)
        if ok:
            score += 1

    ok, msg = manual_check_no_leakage(agent_dir)
    results.append(msg)
    if ok:
        score += 1

    # Second manual check: seed in code
    # Only deducts a point if it fails - keeps max score at 5
    ok2, msg2 = manual_check_seed_in_code(agent_dir)
    results.append(msg2)
    if not ok2 and score > 0:
        score -= 1
        results[-1] = msg2 + " [deducted 1 point]"

    return min(max(score, 0), MAX_SCORE), results


# ---------------------------------------------------------------------------
# CSV append
# ---------------------------------------------------------------------------

def append_to_scores(agent_name: str, tool: str, score: int,
                     time_mins: float, notes: str, failure: str) -> None:
    SCORES_CSV.parent.mkdir(parents=True, exist_ok=True)
    write_header = not SCORES_CSV.exists() or SCORES_CSV.stat().st_size == 0
    with open(SCORES_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                "agent_name", "tool", "task_id",
                "score_0_to_5", "time_mins", "notes", "failure_mode"
            ])
        writer.writerow([agent_name, tool, TASK_ID, score, time_mins, notes, failure])
    print(f"\nRow appended to {SCORES_CSV}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Task 03 - Baseline Model")
    parser.add_argument("--agent", required=True,
                        help="Path to agent task folder, e.g. agents/antigravity/task_03/")
    parser.add_argument("--outputs", default="outputs",
                        help="Name of outputs subfolder (default: outputs). "
                             "Use 'outputs_claude' for Claude, 'output_03_codex' for Codex.")
    parser.add_argument("--name", required=True, help="Your name")
    parser.add_argument("--tool", required=True, help="Tool used")
    parser.add_argument("--time", required=True, type=float, help="Time spent in minutes")
    parser.add_argument("--notes", default="", help="Brief notes")
    parser.add_argument("--failure", default="none", help="Failure mode or 'none'")
    args = parser.parse_args()

    agent_dir = Path(args.agent)
    if not agent_dir.exists():
        print(f"ERROR: agent directory not found: {agent_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Evaluating : {agent_dir}")
    print(f"Outputs in : {args.outputs}/")
    print(f"Scorer     : {args.name}  |  Tool: {args.tool}")
    print(f"{'='*60}\n")

    score, results = run_evaluation(agent_dir, args.outputs)

    print("\n--- Results ---")
    for line in results:
        print(" ", line)
    print(f"\nFinal score: {score} / {MAX_SCORE}")

    append_to_scores(args.name, args.tool, score, args.time, args.notes, args.failure)


if __name__ == "__main__":
    main()
