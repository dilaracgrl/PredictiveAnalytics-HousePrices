"""
evaluate.py - Task 04: Improving Performance
Shared scoring script. All agents run their outputs through this file.

Usage:
    python tasks/task_04_improving_performance/evaluate.py \
        --agent agents/antigravity/task_04/ \
        --name caroline --tool "Antigravity" \
        --time 35 --notes "histgradientboost" --failure "none"

    # For agents with renamed output folders:
    python tasks/task_04_improving_performance/evaluate.py \
        --agent agents/claude/task_04_claude/ \
        --outputs outputs_claude \
        --name dilara --tool "Claude (claude.ai)" \
        --time 40 --notes "..." --failure "..."
"""

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd

SCORES_CSV = Path("results/scores.csv")
TASK_ID = "task_04_improving_performance"
MAX_SCORE = 5

# A meaningful improvement must exceed 1% on at least one metric.
# This filters out rounding-error deltas and trivially marginal changes.
MIN_MEANINGFUL_DELTA_PCT = 1.0


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

def check_improved_results_csv(outputs_dir: Path) -> tuple[bool, str]:
    f = outputs_dir / "improved_results.csv"
    if not f.exists():
        return False, "FAIL - improved_results.csv not found in outputs folder"
    try:
        df = pd.read_csv(f)
    except Exception as e:
        return False, f"FAIL - could not read improved_results.csv: {e}"
    if len(df) == 0:
        return False, "FAIL - improved_results.csv is empty"
    has_baseline = any(c in df.columns for c in
                       ["baseline_value", "baseline", "base_value"])
    has_improved = any(c in df.columns for c in
                       ["improved_value", "improved", "new_value"])
    if has_baseline and has_improved:
        return True, (f"PASS - improved_results.csv present with "
                      f"baseline and improved columns ({list(df.columns)})")
    return False, (f"FAIL - improved_results.csv must contain both a baseline and "
                   f"improved value column. Found: {list(df.columns)}")


def check_meaningful_improvement(outputs_dir: Path) -> tuple[bool, str]:
    f = outputs_dir / "improved_results.csv"
    if not f.exists():
        return False, "SKIP - improved_results.csv not found"
    try:
        df = pd.read_csv(f)
    except Exception as e:
        return False, f"FAIL - could not read file: {e}"

    # Try delta_pct column first
    for pct_col in ["delta_pct", "pct_change", "improvement_pct"]:
        if pct_col in df.columns:
            max_pct = df[pct_col].abs().max()
            if max_pct >= MIN_MEANINGFUL_DELTA_PCT:
                return True, (f"PASS - max delta = {max_pct:.2f}% "
                               f"(above {MIN_MEANINGFUL_DELTA_PCT}% threshold)")
            return False, (f"FAIL - max delta = {max_pct:.2f}% "
                           f"(below {MIN_MEANINGFUL_DELTA_PCT}% threshold; "
                           f"improvement is within noise)")

    # Fall back: compute % change from baseline vs improved columns
    for b_col, i_col in [("baseline_value", "improved_value"),
                          ("baseline", "improved"),
                          ("base_value", "new_value")]:
        if b_col in df.columns and i_col in df.columns:
            baseline = df[b_col].abs()
            delta_pct = ((df[i_col] - df[b_col]).abs() / baseline.replace(0, 1) * 100)
            max_pct = delta_pct.max()
            if max_pct >= MIN_MEANINGFUL_DELTA_PCT:
                return True, (f"PASS - max improvement = {max_pct:.2f}% "
                               f"(above {MIN_MEANINGFUL_DELTA_PCT}% threshold)")
            return False, (f"FAIL - max improvement = {max_pct:.2f}% "
                           f"(below {MIN_MEANINGFUL_DELTA_PCT}% threshold)")

    return False, "FAIL - could not compute improvement delta from improved_results.csv"


def check_improved_model_file(outputs_dir: Path) -> tuple[bool, str]:
    pkl_files = list(outputs_dir.glob("improved*.pkl")) + list(outputs_dir.glob("*.pkl"))
    if pkl_files:
        return True, f"PASS - model file present: {[f.name for f in pkl_files[:2]]}"
    return False, "FAIL - no .pkl model file found in outputs folder"


def check_improvement_report(outputs_dir: Path) -> tuple[bool, str]:
    f = outputs_dir / "improvement_report.md"
    if not f.exists():
        return False, "FAIL - improvement_report.md not found in outputs folder"
    content = f.read_text()
    content_lower = content.lower()

    if len(content.strip()) < 200:
        return False, "FAIL - improvement_report.md too short to contain substantive justification"

    # Must name a specific technique
    has_technique = any(w in content_lower for w in [
        "histgradientboosting", "randomforest", "gradientboosting",
        "xgboost", "lightgbm", "catboost", "targetencoder",
        "feature engineering", "hyperparameter", "cross-validation",
        "log transform", "log1p", "polynomial"
    ])

    # Must document the leakage check explicitly
    has_leakage_check = any(w in content_lower for w in [
        "leakage", "leak", "fitted on train", "fit on train",
        "transform only", "pipeline"
    ])

    failures = []
    if not has_technique:
        failures.append("no specific improvement technique named")
    if not has_leakage_check:
        failures.append("no explicit leakage confirmation")
    if failures:
        return False, f"FAIL - improvement_report.md: {'; '.join(failures)}"
    return True, "PASS - improvement_report.md names technique and confirms no leakage"


# ---------------------------------------------------------------------------
# Manual checks
# ---------------------------------------------------------------------------

def manual_check_no_leakage(agent_dir: Path) -> tuple[bool, str]:
    print("\n[MANUAL CHECK 1 of 2] Open the Task 04 notebook.")
    print("Question: Are ALL new preprocessing steps (target encoding, feature")
    print("          engineering, new scalers) fitted on training data only,")
    print("          with no test-set target values used at any point?")
    answer = input("Enter y/n: ").strip().lower()
    if answer == "y":
        return True, "PASS (manual) - no new leakage introduced"
    return False, "FAIL (manual) - new leakage detected in improvement pipeline"


def manual_check_failure_documented(outputs_dir: Path) -> tuple[bool, str]:
    print("\n[MANUAL CHECK 2 of 2] Read improvement_report.md.")
    print("Question: Does the report document at least one approach that was")
    print("          tried and did NOT work, or explain why alternatives were")
    print("          rejected? (A report that only describes the successful")
    print("          approach fails this check.)")
    answer = input("Enter y/n: ").strip().lower()
    if answer == "y":
        return True, "PASS (manual) - failed approaches documented"
    return False, "FAIL (manual) - report only describes success; no rejected approaches recorded"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def run_evaluation(agent_dir: Path, outputs_name: str) -> tuple[int, list[str]]:
    outputs_dir = find_outputs(agent_dir, outputs_name)
    results = []
    score = 0

    for check_fn in [check_improved_results_csv, check_meaningful_improvement,
                     check_improved_model_file, check_improvement_report]:
        ok, msg = check_fn(outputs_dir)
        results.append(msg)
        if ok:
            score += 1

    ok, msg = manual_check_no_leakage(agent_dir)
    results.append(msg)
    if ok:
        score += 1

    # Second manual check: failed approaches documented
    # Deducts a point if missing - critical for benchmarking evidence
    ok2, msg2 = manual_check_failure_documented(outputs_dir)
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
    parser = argparse.ArgumentParser(description="Evaluate Task 04 - Improving Performance")
    parser.add_argument("--agent", required=True,
                        help="Path to agent task folder, e.g. agents/antigravity/task_04/")
    parser.add_argument("--outputs", default="outputs",
                        help="Name of outputs subfolder (default: outputs). "
                             "Use 'outputs_claude' for Claude, 'output_04_codex' for Codex.")
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
