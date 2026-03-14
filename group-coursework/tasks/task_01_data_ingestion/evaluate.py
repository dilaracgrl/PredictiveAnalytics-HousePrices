"""
evaluate.py — Task 01: Data Ingestion
Shared scoring script. All agents run their outputs through this file.

Usage:
    python tasks/task_01_data_ingestion/evaluate.py \
        --agent agents/claude/task_01/ \
        --name <your_name> --tool "Claude (claude.ai)" \
        --time 25 --notes "clean output" --failure "none"
"""

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd

SCORES_CSV = Path("results/scores.csv")
TASK_ID = "task_01_data_ingestion"
MAX_SCORE = 5


# ---------------------------------------------------------------------------
# Automated checks
# ---------------------------------------------------------------------------

def check_ingested_csv(agent_dir: Path) -> tuple[bool, str]:
    f = agent_dir / "outputs" / "ingested.csv"
    if f.exists():
        return True, "PASS — ingested.csv present in outputs/"
    return False, "FAIL — ingested.csv not found in outputs/"


def check_no_missing_values(agent_dir: Path) -> tuple[bool, str]:
    f = agent_dir / "outputs" / "ingested.csv"
    if not f.exists():
        return False, "SKIP — ingested.csv not found"
    try:
        df = pd.read_csv(f)
    except Exception as e:
        return False, f"FAIL — could not read ingested.csv: {e}"
    total_missing = df.isnull().sum().sum()
    if total_missing == 0:
        return True, "PASS — no missing values in ingested.csv"
    detail = df.isnull().sum()[df.isnull().sum() > 0].to_dict()
    return False, f"FAIL — {total_missing} missing value(s) remain: {detail}"


def check_schema_log(agent_dir: Path) -> tuple[bool, str]:
    f = agent_dir / "outputs" / "schema_log.md"
    if not f.exists():
        return False, "FAIL — schema_log.md not found in outputs/"
    content = f.read_text()
    # Check that it contains at least column names, dtypes, and row count
    required_keywords = ["dtype", "row"]
    missing = [kw for kw in required_keywords if kw.lower() not in content.lower()]
    if missing:
        return False, f"FAIL — schema_log.md missing expected content: {missing}"
    return True, "PASS — schema_log.md present and contains schema information"


def check_missingness_report(agent_dir: Path) -> tuple[bool, str]:
    f = agent_dir / "outputs" / "missingness_report.md"
    if not f.exists():
        return False, "FAIL — missingness_report.md not found in outputs/"
    content = f.read_text()
    # Should mention either "no missing" or contain a handling strategy section
    has_content = len(content.strip()) > 50
    has_strategy = "strategy" in content.lower() or "no missing" in content.lower()
    if has_content and has_strategy:
        return True, "PASS — missingness_report.md present with content"
    return False, "FAIL — missingness_report.md too sparse or missing handling strategy"


# ---------------------------------------------------------------------------
# Manual prompt
# ---------------------------------------------------------------------------

def manual_check_assumptions(agent_dir: Path) -> tuple[bool, str]:
    print("\n[MANUAL CHECK] Open agents/<agent>/task_01/outputs/missingness_report.md")
    print("Question: Does every imputation or drop decision have a written justification?")
    answer = input("Enter y/n: ").strip().lower()
    if answer == "y":
        return True, "PASS (manual) — assumptions documented"
    return False, "FAIL (manual) — assumptions not sufficiently documented"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def run_evaluation(agent_dir: Path) -> tuple[int, list[str]]:
    results = []
    score = 0

    for check_fn in [check_ingested_csv, check_no_missing_values,
                     check_schema_log, check_missingness_report]:
        ok, msg = check_fn(agent_dir)
        results.append(msg)
        if ok:
            score += 1

    ok, msg = manual_check_assumptions(agent_dir)
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
    parser = argparse.ArgumentParser(description="Evaluate Task 01 — Data Ingestion")
    parser.add_argument("--agent", required=True,
                        help="Path to agent task folder, e.g. agents/claude/task_01/")
    parser.add_argument("--name", required=True, help="Your name")
    parser.add_argument("--tool", required=True,
                        help="Tool used, e.g. 'Claude (claude.ai)'")
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
