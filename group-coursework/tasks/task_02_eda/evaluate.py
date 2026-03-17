"""
evaluate.py - Task 02: EDA and Insight Generation
Shared scoring script. All agents run their outputs through this file.

Usage:
    python tasks/task_02_eda/evaluate.py \
        --agent agents/antigravity/task_02/ \
        --name caroline --tool "Antigravity" \
        --time 20 --notes "3 plots, eda_summary written" --failure "none"

    # For agents with renamed output folders:
    python tasks/task_02_eda/evaluate.py \
        --agent agents/claude/task_02_claude/ \
        --outputs outputs_claude \
        --name dilara --tool "Claude (claude.ai)" \
        --time 25 --notes "..." --failure "..."
"""

import argparse
import csv
import json
import sys
from pathlib import Path

SCORES_CSV = Path("results/scores.csv")
TASK_ID = "task_02_eda"
MAX_SCORE = 5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_outputs(agent_dir: Path, outputs_name: str) -> Path:
    """Return the outputs folder, checking agent root and subfolders."""
    direct = agent_dir / outputs_name
    if direct.exists():
        return direct
    # also check one level up in case agent_dir is already inside task folder
    for sub in agent_dir.iterdir():
        candidate = sub / outputs_name
        if candidate.exists():
            return candidate
    return direct  # return even if missing so checks can report FAIL


def find_notebook(agent_dir: Path, outputs_dir: Path):
    """Find any .ipynb in the agent task folder or outputs folder."""
    nbs = list(agent_dir.glob("*.ipynb")) + list(outputs_dir.glob("*.ipynb"))
    return nbs


# ---------------------------------------------------------------------------
# Automated checks
# ---------------------------------------------------------------------------

def check_plots(outputs_dir: Path) -> tuple[bool, str]:
    if not outputs_dir.exists():
        return False, f"FAIL - outputs folder not found: {outputs_dir}"
    pngs = list(outputs_dir.glob("*.png")) + list(outputs_dir.glob("*.pdf"))
    if len(pngs) >= 3:
        return True, f"PASS - {len(pngs)} plot file(s) found"
    return False, f"FAIL - {len(pngs)} plot file(s) found, need at least 3"


def check_eda_summary(outputs_dir: Path) -> tuple[bool, str]:
    f = outputs_dir / "eda_summary.md"
    if not f.exists():
        return False, "FAIL - eda_summary.md not found in outputs folder"
    content = f.read_text().lower()
    if len(content.strip()) < 150:
        return False, "FAIL - eda_summary.md too short to contain substantive findings"
    # Must reference the target variable and at least one specific feature
    has_target = any(w in content for w in ["price", "target"])
    has_feature = any(w in content for w in [
        "room_type", "neighbourhood", "borough", "minimum_nights",
        "availability", "correlation", "distribution", "skew"
    ])
    has_insight = any(w in content for w in [
        "suggests", "indicates", "implies", "therefore", "because",
        "higher", "lower", "significant", "dominant", "weak", "strong"
    ])
    failures = []
    if not has_target:
        failures.append("no reference to target variable (price)")
    if not has_feature:
        failures.append("no reference to any specific feature")
    if not has_insight:
        failures.append("no interpretive language -- reads as plot description not insight")
    if failures:
        return False, f"FAIL - eda_summary.md: {'; '.join(failures)}"
    return True, "PASS - eda_summary.md contains substantive findings"


def check_notebook_present(agent_dir: Path, outputs_dir: Path) -> tuple[bool, str]:
    nbs = find_notebook(agent_dir, outputs_dir)
    if nbs:
        return True, f"PASS - notebook present ({nbs[0].name})"
    return False, "FAIL - no .ipynb found in task folder or outputs folder"


def check_cells_cleared(agent_dir: Path, outputs_dir: Path) -> tuple[bool, str]:
    nbs = find_notebook(agent_dir, outputs_dir)
    if not nbs:
        return False, "SKIP - no notebook found to check"
    nb_path = nbs[0]
    try:
        with open(nb_path, encoding="utf-8") as f:
            nb = json.load(f)
    except Exception as e:
        return False, f"FAIL - could not read notebook: {e}"
    cells_with_output = sum(
        1 for cell in nb.get("cells", [])
        if cell.get("outputs")
    )
    if cells_with_output == 0:
        return True, "PASS - all notebook cells are cleared"
    return False, (f"FAIL - {cells_with_output} cell(s) still have outputs; "
                   "run Kernel > Restart & Clear Output before committing")


# ---------------------------------------------------------------------------
# Manual checks
# ---------------------------------------------------------------------------

def manual_check_no_leakage(agent_dir: Path) -> tuple[bool, str]:
    print("\n[MANUAL CHECK 1 of 2] Open the EDA notebook and check cell order.")
    print("Question: Is the train/test split the FIRST operation after loading data,")
    print("          before any plots, statistics, or value_counts()?")
    answer = input("Enter y/n: ").strip().lower()
    if answer == "y":
        return True, "PASS (manual) - no test-set leakage detected"
    return False, "FAIL (manual) - EDA uses test data or full dataset before split"


def manual_check_insights(outputs_dir: Path) -> tuple[bool, str]:
    print("\n[MANUAL CHECK 2 of 2] Read outputs/eda_summary.md carefully.")
    print("Question: Does every plot have a written interpretation that explains")
    print("          what the pattern means for modelling, not just what it shows?")
    answer = input("Enter y/n: ").strip().lower()
    if answer == "y":
        return True, "PASS (manual) - insights are substantive and modelling-relevant"
    return False, "FAIL (manual) - summary describes plots rather than interpreting them"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def run_evaluation(agent_dir: Path, outputs_name: str) -> tuple[int, list[str]]:
    outputs_dir = find_outputs(agent_dir, outputs_name)
    results = []
    score = 0

    for check_fn, args in [
        (check_plots,            (outputs_dir,)),
        (check_eda_summary,      (outputs_dir,)),
        (check_notebook_present, (agent_dir, outputs_dir)),
        (check_cells_cleared,    (agent_dir, outputs_dir)),
    ]:
        ok, msg = check_fn(*args)
        results.append(msg)
        if ok:
            score += 1

    ok, msg = manual_check_no_leakage(agent_dir)
    results.append(msg)
    if ok:
        score += 1

    # Insights quality replaces one automated point to keep max at 5
    # Only called if automated checks pass - reduces gaming
    ok2, msg2 = manual_check_insights(outputs_dir)
    results.append(msg2)
    # Insights check modifies the score only if it fails (deduct 1)
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
    parser = argparse.ArgumentParser(description="Evaluate Task 02 - EDA")
    parser.add_argument("--agent", required=True,
                        help="Path to agent task folder, e.g. agents/antigravity/task_02/")
    parser.add_argument("--outputs", default="outputs",
                        help="Name of outputs subfolder (default: outputs). "
                             "Use 'outputs_claude' for Claude, 'output_02_codex' for Codex.")
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
