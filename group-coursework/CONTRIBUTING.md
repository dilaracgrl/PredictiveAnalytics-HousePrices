# Contributing Guide

This document defines the rules for working in this repository. All team members must follow these rules without exception. Violations will corrupt the shared experiment.

---

## The Seven Rules

### Rule 1 — `data/raw/` is immutable
Never modify, overwrite, or delete any file inside `data/raw/`. It contains the original dataset as downloaded. All outputs go to your agent's `outputs/` folder.

### Rule 2 — Never edit another agent's folder
Each team member owns their agent folder. Only touch `agents/<your_agent>/`. Do not open, edit, or move files inside `agents/claude/`, `agents/codex/`, or `agents/antigravity/` unless you are the person running that agent.

### Rule 3 — All agents must run `evaluate.py`
Every task has one shared `tasks/task_XX_<name>/evaluate.py`. Run it against your outputs before marking a task as done. This populates `results/scores.csv` and makes cross-agent comparison valid.

### Rule 4 — `scores.csv` schema is fixed
`results/scores.csv` uses exactly this schema — do not add, remove, or rename columns:

```
agent_name, tool, task_id, score_0_to_5, time_mins, notes, failure_mode
```

`evaluate.py` appends rows automatically. Do not edit the CSV by hand unless correcting a clear error, and note the correction in a commit message.

### Rule 5 — Branch naming and merge discipline
Branch names must follow the pattern:

```
<your_name>/<agent>/<task>
```

Examples: `<name>/claude/task_01`, `<name>/codex/task_03`

Only merge your own agent's outputs to `main`. Never merge another person's branch. Only merge when `evaluate.py` has been run and a score row exists in `scores.csv`.

### Rule 6 — Clear all notebook output cells before committing
Before every `git add` on a `.ipynb` file:

1. Open the notebook in Jupyter.
2. Go to **Kernel > Restart & Clear Output**.
3. Save.
4. Then commit.

This prevents large binary diffs and avoids accidentally committing API keys or file paths in cell outputs.

### Rule 7 — Relative paths only; `SEED = 42` everywhere
- Never write absolute paths in any script or notebook.
- Set `SEED = 42` at the top of every notebook and script that uses randomness.

These two rules are the minimum requirement for reproducibility.

---

## Workflow Summary

```bash
# 1. Create your branch
git checkout -b <your_name>/claude/task_01

# 2. Do the work — save outputs to agents/claude/task_01/outputs/

# 3. Score your work
python tasks/task_01_data_ingestion/evaluate.py \
  --agent agents/claude/task_01/ \
  --name <your_name> --tool "Claude (claude.ai)" \
  --time 25 --notes "clean output" --failure "none"

# 4. Stage only your files
git add agents/claude/task_01/ results/scores.csv

# 5. Commit and push
git commit -m "<name>: task_01 claude — score 4/5"
git push -u origin <your_name>/claude/task_01

# 6. Open a PR into main — tag a teammate to review
```

---

## What Counts as a Merge Conflict Risk?

| File | Risk | How to avoid |
|------|------|--------------|
| `results/scores.csv` | Two people append at the same time | Only append via `evaluate.py`; resolve conflicts by keeping both rows |
| `playbook.md` | Multiple edits | Coordinate via PR descriptions; use dated entries |
| `report/draft.md` | Concurrent section edits | Assign sections to individuals |
| `agents/*/` | Editing someone else's folder | **Never do this** |
