"""
evaluate.py - Task 03: Baseline Model
Shared scoring script. All agents run their outputs through this file.

Usage:
    python tasks/task_03_baseline_model/evaluate.py \
        --agent agents/antigravity/task_03/ \
        --name <your_name> --tool "Antigravity" \
        --time 30 --notes "ridge regression baseline" --failure "none"
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import pandas as pd

SCORES_CSV = Path("results/scores.csv")
TASK_ID = "task_03_baseline_model"
MAX_SCORE = 5


# ---------------------------------------------------------------------------
# Automated checks
# ---------------------------------------------------------------------------

def check_baseline_results_csv(agent_dir: Path) -> tuple[bool, str]:
    f = agent_dir / "outputs" / "baseline_results.csv"
    if not f.exists():
        return False, "FAIL - baseline_results.csv not found in outputs/"
    try:
        df = pd.read_csv(f)
    except Exception as e:
        return False, f"FAIL - could not read baseline_results.csv: {e}"
    if len(df) == 0:
        return False, "FAIL - baseline_results.csv is empty"
    if df.isnull().sum().sum() > 0:
        return False, "FAIL - baseline_results.csv contains null values"
    return True, f"PASS - baseline_results.csv present with {len(df)} row(s)"


def check_two_metrics(agent_dir: Path) -> tuple[bool, str]:
    f = agent_dir / "outputs" / "baseline_results.csv"
    if not f.exists():
        return False, "SKIP - baseline_results.csv not found"
    try:
        df = pd.read_csv(f)
    except Exception as e:
        return False, f"FAIL - could not read baseline_results.csv: {e}"
    metric_col = None
    for col in ["metric_name", "metric"]:
        if col in df.columns:
            metric_col = col
            break
    if metric_col is None:
        return False, "FAIL - no metric_name column found in baseline_results.csv"
    n_metrics = df[metric_col].nunique()
    if n_metrics >= 2:
        return True, f"PASS - {n_metrics} distinct metric(s) reported"
    return False, f"FAIL - only {n_metrics} metric(s) reported, need at least 2"


def check_model_pkl(agent_dir: Path) -> tuple[bool, str]:
    f = agent_dir / "outputs" / "model.pkl"
    if f.exists():
        return True, "PASS - model.pkl present in outputs/"
    return False, "FAIL - model.pkl not found in outputs/"


def check_baseline_report(agent_dir: Path) -> tuple[bool, str]:
    f = agent_dir / "outputs" / "baseline_report.md"
    if not f.exists():
        return False, "FAIL - baseline_report.md not found in outputs/"
    content = f.read_text()
    has_seed = "42" in content or "seed" in content.lower()
    has_split = "split" in content.lower() or "80" in content or "train" in content.lower()
    if has_seed and has_split:
        return True, "PASS - baseline_report.md present with seed and split documentation"
    missing = []
    if not has_seed:
        missing.append("SEED=42")
    if not has_split:
        missing.append("split details")
    return False, f"FAIL - baseline_report.md missing: {', '.join(missing)}"


# ---------------------------------------------------------------------------
# Manual check
# ---------------------------------------------------------------------------

def manual_check_no_leakage(agent_dir: Path) -> tuple[bool, str]:
    print("\n[MANUAL CHECK] Open the Task 03 notebook.")
    print("Question: Are all scalers and encoders fitted on training data only,")
    print("          with .transform() called separately on val/test?")
    answer = input("Enter y/n: ").strip().lower()
    if answer == "y":
        return True, "PASS (manual) - no preprocessing leakage detected"
    return False, "FAIL (manual) - scaler or encoder appears fitted on full dataset or test set"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def run_evaluation(agent_dir: Path) -> tuple[int, list[str]]:
    results = []
    score = 0

    for check_fn in [check_baseline_results_csv, check_two_metrics,
                     check_model_pkl, check_baseline_report]:
        ok, msg = check_fn(agent_dir)
        results.append(msg)
        if ok:
            score += 1

    ok, msg = manual_check_no_leakage(agent_dir)
    results.append(msg)
    if ok:
        score += 1

    return min(score, MAX_SCORE), results


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
    parser.add_argument("--name", required=True, help="Your name")
    parser.add_argument("--tool", required=True,
                        help="Tool used, e.g. 'Antigravity'")
    parser.add_argument("--time", required=True, type=float,
                        help="Time spent in minutes")
    parser.add_argument("--notes", default="", help="Brief notes on the run")
    parser.add_argument("--failure", default="none",
                        help="Failure mode observed, or 'none'")
    args = parser.parse_args()

    agent_dir = Path(args.agent)
    if not agent_dir.exists():
        print(f"ERROR: agent directory not found: {agent_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Evaluating: {agent_dir}")
    print(f"Scorer    : {args.name}  |  Tool: {args.tool}")
    print(f"{'='*60}\n")

    score, results = run_evaluation(agent_dir)

    print("\n--- Results ---")
    for line in results:
        print(" ", line)
    print(f"\nFinal score: {score} / {MAX_SCORE}")

    append_to_scores(args.name, args.tool, score, args.time, args.notes, args.failure)


if __name__ == "__main__":
    main()
