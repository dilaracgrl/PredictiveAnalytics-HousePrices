"""
evaluate.py - Task 04: Improving Performance
Shared scoring script. All agents run their outputs through this file.

Usage:
    python tasks/task_04_improving_performance/evaluate.py \
        --agent agents/antigravity/task_04/ \
        --name <your_name> --tool "Antigravity" \
        --time 35 --notes "gradient boosted model" --failure "none"
"""

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd

SCORES_CSV = Path("results/scores.csv")
TASK_ID = "task_04_improving_performance"
MAX_SCORE = 5

# Minimum absolute delta to count as a meaningful improvement.
# Prevents rounding-error deltas from being claimed as improvements.
MIN_MEANINGFUL_DELTA = 0.01


# ---------------------------------------------------------------------------
# Automated checks
# ---------------------------------------------------------------------------

def check_improved_results_csv(agent_dir: Path) -> tuple[bool, str]:
    f = agent_dir / "outputs" / "improved_results.csv"
    if not f.exists():
        return False, "FAIL - improved_results.csv not found in outputs/"
    try:
        df = pd.read_csv(f)
    except Exception as e:
        return False, f"FAIL - could not read improved_results.csv: {e}"
    if len(df) == 0:
        return False, "FAIL - improved_results.csv is empty"
    # Check that both baseline and improved values are present
    has_baseline = any(c in df.columns for c in
                       ["baseline_value", "baseline", "base_value"])
    has_improved = any(c in df.columns for c in
                       ["improved_value", "improved", "new_value", "value"])
    if has_baseline and has_improved:
        return True, "PASS - improved_results.csv present with baseline and improved columns"
    return False, ("FAIL - improved_results.csv missing baseline or improved value columns. "
                   f"Found: {list(df.columns)}")


def check_meaningful_improvement(agent_dir: Path) -> tuple[bool, str]:
    f = agent_dir / "outputs" / "improved_results.csv"
    if not f.exists():
        return False, "SKIP - improved_results.csv not found"
    try:
        df = pd.read_csv(f)
    except Exception as e:
        return False, f"FAIL - could not read improved_results.csv: {e}"
    # Look for a delta or pct column
    delta_col = None
    for col in ["delta_pct", "delta", "improvement", "change"]:
        if col in df.columns:
            delta_col = col
            break
    if delta_col is not None:
        max_delta = df[delta_col].abs().max()
        if max_delta > MIN_MEANINGFUL_DELTA:
            return True, f"PASS - max absolute delta = {max_delta:.4f} (above noise threshold)"
        return False, f"FAIL - max absolute delta = {max_delta:.4f} (below noise threshold of {MIN_MEANINGFUL_DELTA})"
    # Fall back: compare baseline_value and improved_value columns directly
    for b_col, i_col in [("baseline_value", "improved_value"),
                          ("baseline", "improved"),
                          ("base_value", "new_value")]:
        if b_col in df.columns and i_col in df.columns:
            delta = (df[i_col] - df[b_col]).abs().max()
            if delta > MIN_MEANINGFUL_DELTA:
                return True, f"PASS - max absolute improvement = {delta:.4f}"
            return False, f"FAIL - max absolute improvement = {delta:.4f} (below noise threshold)"
    return False, "FAIL - could not compute delta from improved_results.csv columns"


def check_improved_model_pkl(agent_dir: Path) -> tuple[bool, str]:
    f = agent_dir / "outputs" / "improved_model.pkl"
    if f.exists():
        return True, "PASS - improved_model.pkl present in outputs/"
    return False, "FAIL - improved_model.pkl not found in outputs/"


def check_improvement_report(agent_dir: Path) -> tuple[bool, str]:
    f = agent_dir / "outputs" / "improvement_report.md"
    if not f.exists():
        return False, "FAIL - improvement_report.md not found in outputs/"
    content = f.read_text()
    has_content = len(content.strip()) > 100
    has_technique = any(kw in content.lower() for kw in
                        ["feature", "tuning", "model", "engineering",
                         "encoder", "gradient", "forest", "hyperparameter"])
    if has_content and has_technique:
        return True, "PASS - improvement_report.md present with technique description"
    return False, "FAIL - improvement_report.md too sparse or missing technique description"


# ---------------------------------------------------------------------------
# Manual checks
# ---------------------------------------------------------------------------

def manual_check_no_leakage(agent_dir: Path) -> tuple[bool, str]:
    print("\n[MANUAL CHECK] Open the Task 04 notebook.")
    print("Question: Are all new preprocessing steps (e.g. encoders, feature engineering)")
    print("          fitted on training data only, with no test-set information used?")
    answer = input("Enter y/n: ").strip().lower()
    if answer == "y":
        return True, "PASS (manual) - no new leakage introduced"
    return False, "FAIL (manual) - new leakage detected in improvement pipeline"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def run_evaluation(agent_dir: Path) -> tuple[int, list[str]]:
    results = []
    score = 0

    for check_fn in [check_improved_results_csv, check_meaningful_improvement,
                     check_improved_model_pkl, check_improvement_report]:
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
    parser = argparse.ArgumentParser(description="Evaluate Task 04 - Improving Performance")
    parser.add_argument("--agent", required=True,
                        help="Path to agent task folder, e.g. agents/antigravity/task_04/")
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
