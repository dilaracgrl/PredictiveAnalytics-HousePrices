"""
evaluate.py - Task 02: EDA and Insight Generation
Shared scoring script. All agents run their outputs through this file.

Usage:
    python tasks/task_02_eda/evaluate.py \
        --agent agents/antigravity/task_02/ \
        --name <your_name> --tool "Antigravity" \
        --time 25 --notes "clean output" --failure "none"
"""

import argparse
import csv
import glob
import sys
from pathlib import Path

SCORES_CSV = Path("results/scores.csv")
TASK_ID = "task_02_eda"
MAX_SCORE = 5


# ---------------------------------------------------------------------------
# Automated checks
# ---------------------------------------------------------------------------

def check_notebook_present(agent_dir: Path) -> tuple[bool, str]:
    notebooks = list(agent_dir.glob("*.ipynb")) + list(
        (agent_dir / "outputs").glob("*.ipynb")
    )
    if notebooks:
        return True, "PASS - notebook present"
    return False, "FAIL - no .ipynb found in task folder or outputs/"


def check_plots(agent_dir: Path) -> tuple[bool, str]:
    outputs = agent_dir / "outputs"
    if not outputs.exists():
        return False, "FAIL - outputs/ folder not found"
    pngs = list(outputs.glob("*.png")) + list(outputs.glob("*.pdf"))
    if len(pngs) >= 3:
        return True, f"PASS - {len(pngs)} plot file(s) found in outputs/"
    return False, f"FAIL - only {len(pngs)} plot file(s) found, need at least 3"


def check_eda_summary(agent_dir: Path) -> tuple[bool, str]:
    f = agent_dir / "outputs" / "eda_summary.md"
    if not f.exists():
        return False, "FAIL - eda_summary.md not found in outputs/"
    content = f.read_text()
    if len(content.strip()) < 100:
        return False, "FAIL - eda_summary.md is too short (under 100 chars)"
    return True, "PASS - eda_summary.md present with content"


def check_cells_cleared(agent_dir: Path) -> tuple[bool, str]:
    import json
    notebooks = list(agent_dir.glob("*.ipynb")) + list(
        (agent_dir / "outputs").glob("*.ipynb")
    )
    if not notebooks:
        return False, "SKIP - no notebook found to check"
    nb_path = notebooks[0]
    try:
        with open(nb_path) as f:
            nb = json.load(f)
    except Exception as e:
        return False, f"FAIL - could not read notebook: {e}"
    for cell in nb.get("cells", []):
        outputs = cell.get("outputs", [])
        if outputs:
            return False, f"FAIL - notebook has {len(outputs)} output(s) in cells; clear before committing"
    return True, "PASS - notebook cells are cleared"


# ---------------------------------------------------------------------------
# Manual checks
# ---------------------------------------------------------------------------

def manual_check_no_leakage(agent_dir: Path) -> tuple[bool, str]:
    print("\n[MANUAL CHECK] Open the EDA notebook and check cell order.")
    print("Question: Is the train/test split performed BEFORE any plots, statistics, or value_counts()?")
    answer = input("Enter y/n: ").strip().lower()
    if answer == "y":
        return True, "PASS (manual) - no test-set leakage detected"
    return False, "FAIL (manual) - EDA appears to use test data or full dataset"


def manual_check_insights(agent_dir: Path) -> tuple[bool, str]:
    print("\n[MANUAL CHECK] Open outputs/eda_summary.md")
    print("Question: Does it contain substantive written findings, not just plot descriptions?")
    answer = input("Enter y/n: ").strip().lower()
    if answer == "y":
        return True, "PASS (manual) - insights are substantive"
    return False, "FAIL (manual) - summary only describes plots without interpretation"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def run_evaluation(agent_dir: Path) -> tuple[int, list[str]]:
    results = []
    score = 0

    for check_fn in [check_plots, check_eda_summary,
                     check_notebook_present, check_cells_cleared]:
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
    parser = argparse.ArgumentParser(description="Evaluate Task 02 - EDA")
    parser.add_argument("--agent", required=True,
                        help="Path to agent task folder, e.g. agents/antigravity/task_02/")
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
