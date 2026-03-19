"""
leakage_check.py — Leakage Detection as a Benchmark Dimension
=============================================================

Turns data-leakage prevention into a measurable, scored metric comparable
across all three agents (Claude, Codex, Antigravity).

Each agent's Task 03 and Task 04 notebooks are parsed programmatically.
Five criteria are checked; each is worth 1 point (max score: 5/5).

RUBRIC
------
  [L1]  train/test split present        — agent splits data at all
  [L2]  split precedes first fit()      — preprocessing not fitted before split
  [L3]  sklearn Pipeline used           — encapsulates all preprocessing steps
  [L4]  no fit() on full X             — no scaler/encoder fitted on un-split data
  [L5]  target encoding handled safely  — TargetEncoder in Pipeline (CV-safe) or
                                          manual encoding computed from train only

Usage
-----
    # Score a single notebook
    python tasks/leakage_check.py --notebook agents/claude/task_03_claude/notebook.ipynb \
        --agent dilara --tool "Claude (claude.ai)" --task task_03_baseline_model

    # Score all agents (batch mode)
    python tasks/leakage_check.py --batch
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

SCORES_CSV = Path("results/scores.csv")
MAX_SCORE = 5
TASK_ID_PREFIX = "leakage_check"


# ─── Data structures ────────────────────────────────────────────────────────

class LeakageResult(NamedTuple):
    score: int
    checks: list   # list of (criterion, passed: bool, detail: str)
    notes: str


# ─── Notebook parser ─────────────────────────────────────────────────────────

def load_code_cells(notebook_path: Path) -> list[str]:
    """Return code-cell source strings in notebook cell order."""
    raw = notebook_path.read_bytes().decode("utf-8-sig")  # handle BOM
    nb = json.loads(raw)
    cells = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            src = cell.get("source", [])
            if isinstance(src, list):
                cells.append("".join(src))
            else:
                cells.append(str(src))
    return cells


def concat_code(cells: list[str]) -> str:
    return "\n".join(cells)


# ─── Leakage detection helpers ───────────────────────────────────────────────

# Patterns that indicate a train/test split (including reuse of saved split indices)
_SPLIT_PATTERNS = [
    r"train_test_split\s*\(",
    r"X_train\s*,\s*X_test",
    r"\.split\s*\(",                    # e.g. KFold.split
    r"split_meta",                      # loading saved split metadata from prior task
    r"train_idx|test_idx",              # saved index arrays
    r"df_train\s*=\s*df\.loc",          # reconstructing train from saved indices
    r"\.loc\s*\[train_idx",             # explicit index-based reconstruction
]

# Patterns that indicate a fit call on a transformer / pipeline
_FIT_PATTERNS = [
    r"\.fit\s*\(",
    r"\.fit_transform\s*\(",
]

# Patterns indicating sklearn Pipeline usage
_PIPELINE_PATTERNS = [
    r"\bPipeline\s*\(",
    r"\bColumnTransformer\s*\(",
]

# Variables that suggest fit is being called on FULL (un-split) data:
#   .fit(X,  or  .fit(df  (not X_train / X_val / X_te)
_FULL_DATA_FIT = re.compile(
    r"\.fit(?:_transform)?\s*\(\s*(?!X_train|X_val|X_test|x_train|x_test"
    r"|df_train|train_df|X_tr\b|X_te\b|Xtrain|Xtest)"
    r"(X\b|df\b|features\b|data\b)",
    re.IGNORECASE,
)

# Patterns indicating target encoding done in a safe way
_SAFE_TARGET_ENC_PATTERNS = [
    r"\bTargetEncoder\s*\(",                      # sklearn TargetEncoder (cross-validated by default)
    r"groupby\s*\(.*\)\s*\[.*\]\s*\.mean\s*\(",  # manual groupby.mean() — scope checked separately
]

# Patterns indicating target encoding applied to full data BEFORE splitting (risky)
# Must NOT appear on df_train / X_train variables
_RISKY_TARGET_ENC_PATTERNS = [
    r"(?<!df_train)(?<!X_train)(?<!train_df)\s*\.groupby\s*\(.*\)\s*\[.*price.*\]\s*\."
    r"(?!.*df_train|.*X_train)",                  # groupby on price on non-train variable
]


def _find_first_pattern(cells: list[str], patterns: list[str]) -> int:
    """Return cell index of first cell matching any pattern, or -1."""
    for i, cell in enumerate(cells):
        for p in patterns:
            if re.search(p, cell, re.IGNORECASE):
                return i
    return -1


def _first_line_matching(cell_src: str, patterns: list[str]) -> int:
    """Return line number within a cell where a pattern first matches, or -1."""
    for lineno, line in enumerate(cell_src.splitlines()):
        for p in patterns:
            if re.search(p, line, re.IGNORECASE):
                return lineno
    return -1


def _any_pattern(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


# ─── Scoring function ─────────────────────────────────────────────────────────

def score_notebook(notebook_path: Path) -> LeakageResult:
    """Analyse a notebook and return a LeakageResult."""
    try:
        cells = load_code_cells(notebook_path)
    except FileNotFoundError:
        return LeakageResult(
            score=0,
            checks=[("notebook_found", False, f"File not found: {notebook_path}")],
            notes="notebook not found",
        )
    except json.JSONDecodeError as e:
        return LeakageResult(
            score=0,
            checks=[("notebook_parsed", False, f"JSON error: {e}")],
            notes="could not parse notebook JSON",
        )

    full_code = concat_code(cells)
    checks = []
    score = 0

    # ── L1: split is present ────────────────────────────────────────────────
    split_cell = _find_first_pattern(cells, _SPLIT_PATTERNS)
    if split_cell >= 0:
        checks.append(("L1_split_present", True,
                        f"PASS — train/test split found (cell {split_cell})"))
        score += 1
    else:
        checks.append(("L1_split_present", False,
                        "FAIL — no train_test_split or X_train/X_test found in notebook"))

    # ── L2: split precedes first fit() ─────────────────────────────────────
    first_fit_cell = _find_first_pattern(cells, _FIT_PATTERNS)
    if split_cell >= 0 and first_fit_cell >= 0:
        if split_cell < first_fit_cell:
            checks.append(("L2_split_before_fit", True,
                            f"PASS — split (cell {split_cell}) precedes first fit() (cell {first_fit_cell})"))
            score += 1
        elif split_cell == first_fit_cell:
            # Both in the same cell — check line ordering within that cell
            split_line = _first_line_matching(cells[split_cell], _SPLIT_PATTERNS)
            fit_line   = _first_line_matching(cells[first_fit_cell], _FIT_PATTERNS)
            if split_line <= fit_line:
                checks.append(("L2_split_before_fit", True,
                                f"PASS — split and first fit() in same cell {split_cell}; "
                                f"split (line {split_line}) precedes fit (line {fit_line})"))
                score += 1
            else:
                checks.append(("L2_split_before_fit", False,
                                f"FAIL — in cell {split_cell}, fit() (line {fit_line}) "
                                f"precedes split (line {split_line})"))
        else:
            checks.append(("L2_split_before_fit", False,
                            f"FAIL — first fit() (cell {first_fit_cell}) precedes split (cell {split_cell}); "
                            "preprocessing fitted before data was split"))
    elif split_cell < 0:
        checks.append(("L2_split_before_fit", False,
                        "SKIP — cannot check ordering; no split detected (L1 failed)"))
    else:
        checks.append(("L2_split_before_fit", False,
                        "FAIL — split found but no fit() call detected at all"))

    # ── L3: sklearn Pipeline used ───────────────────────────────────────────
    if _any_pattern(full_code, _PIPELINE_PATTERNS):
        # Confirm it's actually from sklearn (not a random variable named Pipeline)
        if re.search(r"from sklearn", full_code):
            checks.append(("L3_pipeline_used", True,
                            "PASS — sklearn Pipeline / ColumnTransformer used to encapsulate preprocessing"))
            score += 1
        else:
            checks.append(("L3_pipeline_used", False,
                            "WARN — Pipeline pattern found but sklearn import not confirmed"))
    else:
        checks.append(("L3_pipeline_used", False,
                        "FAIL — no sklearn Pipeline detected; preprocessing steps may be loose"))

    # ── L4: no fit() on full (un-split) X ──────────────────────────────────
    full_data_fits = _FULL_DATA_FIT.findall(full_code)
    if not full_data_fits:
        checks.append(("L4_no_fit_on_full_X", True,
                        "PASS — no fit() calls detected on full (un-split) X or df"))
        score += 1
    else:
        # Check false-positive: could be `Pipeline.fit(X_train)` where X was renamed
        # Be more specific: show the matches
        checks.append(("L4_no_fit_on_full_X", False,
                        f"WARN — possible fit() on full data detected (matched: {full_data_fits[:3]}); "
                        "review manually to confirm leakage"))

    # ── L5: target encoding handled safely ─────────────────────────────────
    has_target_enc = _any_pattern(full_code, _SAFE_TARGET_ENC_PATTERNS)

    # Positively safe: TargetEncoder (sklearn, cross-validated) or explicit train-only groupby
    sklearn_te  = bool(re.search(r"\bTargetEncoder\s*\(", full_code))
    train_groupby = bool(re.search(
        r"(df_train|X_train|train_df)\s*\.groupby", full_code, re.IGNORECASE
    ))
    # Risky: groupby on price-related column on a variable that doesn't look like train-subset
    risky_groupby = bool(re.search(
        r"(?:^|\s)(df|X)\s*\.groupby\s*\(.*\)\s*\[.*price", full_code, re.IGNORECASE | re.MULTILINE
    ))

    if not has_target_enc:
        # No neighbourhood/target encoding — criterion N/A, no leakage risk
        checks.append(("L5_target_enc_safe", True,
                        "PASS — no target encoding used; criterion not applicable (no leakage risk)"))
        score += 1
    elif sklearn_te:
        checks.append(("L5_target_enc_safe", True,
                        "PASS — sklearn TargetEncoder used (cross-validated within Pipeline; "
                        "prevents internal target leakage by design)"))
        score += 1
    elif train_groupby and not risky_groupby:
        checks.append(("L5_target_enc_safe", True,
                        "PASS — manual target encoding computed on df_train/X_train only "
                        "(train-only groupby detected; test set not used for encoding)"))
        score += 1
    elif risky_groupby:
        checks.append(("L5_target_enc_safe", False,
                        "FAIL — target encoding appears to use full df/X before split; "
                        "this leaks target information from test rows into training features"))
    else:
        checks.append(("L5_target_enc_safe", False,
                        "WARN — target encoding detected but training-data scope unclear; "
                        "verify encoding is computed from training data only"))

    notes_parts = [f"{c[0]}={'✓' if c[1] else '✗'}" for c in checks]
    notes = f"score={score}/5 | " + " | ".join(notes_parts)
    return LeakageResult(score=score, checks=checks, notes=notes)


# ─── Batch configuration ─────────────────────────────────────────────────────

# Each entry: (agent_name, tool, task_label, notebook_path_relative_to_repo_root)
BATCH_AGENTS = [
    # Claude
    (
        "dilara", "Claude (claude.ai)", "task_03",
        "agents/claude/task_03_claude/notebook.ipynb",
    ),
    (
        "dilara", "Claude (claude.ai)", "task_04",
        "agents/claude/task_04_claude/notebook.ipynb",
    ),
    # Antigravity
    (
        "caroline", "Antigravity", "task_03",
        "agents/antigravity/task_03/task_03_antigravity.ipynb",
    ),
    (
        "caroline", "Antigravity", "task_04",
        "agents/antigravity/task_04/task_04_antigravity.ipynb",
    ),
    # Codex
    (
        "moham", "Codex", "task_03",
        "agents/codex/task_03_codex/task_03_baseline.ipynb",
    ),
    (
        "moham", "Codex", "task_04",
        "agents/codex/task_04_codex/task_04_improvement.ipynb",
    ),
]


# ─── CSV append ──────────────────────────────────────────────────────────────

def append_to_scores(agent_name: str, tool: str, task_label: str,
                     score: int, notes: str) -> None:
    task_id = f"{TASK_ID_PREFIX}_{task_label}"
    SCORES_CSV.parent.mkdir(parents=True, exist_ok=True)
    write_header = not SCORES_CSV.exists() or SCORES_CSV.stat().st_size == 0
    with open(SCORES_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                "agent_name", "tool", "task_id",
                "score_0_to_5", "time_mins", "notes", "failure_mode",
            ])
        failure = "none" if score == MAX_SCORE else "leakage_risk_detected"
        writer.writerow([agent_name, tool, task_id, score, 0, notes, failure])
    print(f"  → Appended to {SCORES_CSV}")


# ─── Print helpers ───────────────────────────────────────────────────────────

def print_result(label: str, result: LeakageResult) -> None:
    bar = "█" * result.score + "░" * (MAX_SCORE - result.score)
    print(f"\n  {label}")
    print(f"  Score : {result.score}/{MAX_SCORE}  [{bar}]")
    for _, passed, detail in result.checks:
        icon = "✓" if passed else "✗"
        print(f"    {icon}  {detail}")


def print_summary_table(results: list) -> None:
    """Print a comparison table of all agent leakage scores."""
    print("\n" + "=" * 70)
    print(f"{'LEAKAGE PREVENTION BENCHMARK':^70}")
    print("=" * 70)
    header = f"{'Agent':<12} {'Tool':<22} {'Task':<10} {'Score':>7}  {'Outcome'}"
    print(header)
    print("-" * 70)
    for agent, tool, task, result in results:
        outcome = "CLEAN" if result.score == MAX_SCORE else f"REVIEW ({result.score}/{MAX_SCORE})"
        print(f"{agent:<12} {tool:<22} {task:<10} {result.score:>3}/{MAX_SCORE}   {outcome}")
    print("=" * 70)

    all_scores = [r.score for _, _, _, r in results]
    print(f"\n  Mean leakage score : {sum(all_scores)/len(all_scores):.2f} / {MAX_SCORE}")
    perfect = sum(1 for s in all_scores if s == MAX_SCORE)
    print(f"  Perfect scores     : {perfect} / {len(all_scores)} notebooks")


# ─── CLI ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Leakage detection scorer — turns leakage prevention into a measurable benchmark dimension"
    )
    subparsers = parser.add_subparsers(dest="mode")

    # Single notebook mode
    single = subparsers.add_parser("single", help="Score one notebook")
    single.add_argument("--notebook", required=True, help="Path to .ipynb file")
    single.add_argument("--agent",   required=True, help="Agent name")
    single.add_argument("--tool",    required=True, help="Tool name")
    single.add_argument("--task",    required=True, help="Task label (e.g. task_03)")
    single.add_argument("--save",    action="store_true", help="Append result to scores.csv")

    # Batch mode (default)
    subparsers.add_parser("batch", help="Score all agents (uses hardcoded BATCH_AGENTS list)")

    args = parser.parse_args()

    if args.mode == "single":
        nb_path = Path(args.notebook)
        result = score_notebook(nb_path)
        print_result(f"{args.agent} / {args.tool} / {args.task}", result)
        if args.save:
            append_to_scores(args.agent, args.tool, args.task, result.score, result.notes)

    else:
        # Default: batch
        # Find repo root (parent of group-coursework/)
        repo_root = Path(__file__).resolve().parent.parent.parent
        group_cw  = repo_root / "group-coursework"

        # Change working dir to group-coursework so scores.csv path resolves correctly
        import os
        os.chdir(group_cw)

        print(f"\nLeakage Benchmark — repo root: {repo_root}")
        print(f"Scoring {len(BATCH_AGENTS)} notebooks...\n")

        all_results = []
        for agent_name, tool, task_label, nb_rel in BATCH_AGENTS:
            nb_path = group_cw / nb_rel
            result  = score_notebook(nb_path)
            label   = f"{agent_name} / {tool} / {task_label}"
            print_result(label, result)
            append_to_scores(agent_name, tool, task_label, result.score, result.notes)
            all_results.append((agent_name, tool, task_label, result))

        print_summary_table(all_results)


if __name__ == "__main__":
    main()
