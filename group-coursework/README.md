# Group Coursework — Benchmarking Agentic LLM Tools for Data Science

Comparing **Claude**, **Codex**, and **Antigravity** on four pipeline tasks using a shared dataset, shared scoring scripts, and structured per-agent workspaces.

---

## Folder Structure

```
group-coursework/
├── data/
│   ├── raw/                              ← Original dataset — NEVER MODIFIED
│   └── processed/                        ← Cleaned version, written once then frozen
│
├── tasks/
│   ├── task_01_data_ingestion/
│   │   ├── README.md                     ← Task spec: objective, inputs, outputs, rubric
│   │   ├── evaluate.py                   ← Shared scoring script (same for all agents)
│   │   └── notebook_template.ipynb       ← Starter notebook for this step
│   ├── task_02_eda/
│   ├── task_03_baseline_model/
│   └── task_04_improving_performance/
│
├── agents/
│   ├── claude/
│   │   ├── task_01/outputs/              ← Agent outputs go here
│   │   ├── task_02/outputs/
│   │   ├── task_03/outputs/
│   │   ├── task_04/outputs/
│   │   ├── logs/                         ← Prompt logs, screenshots, raw responses
│   │   └── notes.md                      ← Reflection: what worked, what failed
│   ├── codex/                            ← Same structure
│   └── antigravity/                      ← Same structure
│
├── results/
│   ├── scores.csv                        ← Auto-filled by evaluate.py
│   └── figures/                          ← Comparison charts for the report
│
├── report/
│   ├── draft.md
│   └── references.bib
│
├── playbook.md                           ← Best-practice checklist
├── CONTRIBUTING.md                       ← Rules — read before touching anything
├── requirements.txt
└── README.md
```

---

## Requirements

- **Python 3.9 or later** — type hints in `evaluate.py` and `leakage_check.py` use built-in generics (`list[str]`, `tuple[bool, str]`) which require 3.9+.
- No GPU required. All models run on CPU.

---

## Quickstart

### 1. Clone and install

```bash
git clone <repo-url>
cd PredictiveAnalytics-HousePrices-1/group-coursework
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Dataset

The raw dataset (`data/raw/AB_NYC_2019.csv`) is already committed to the repository — no download needed after cloning.

If you need to obtain it independently (e.g. for a fresh copy):
```bash
# Option A — Kaggle CLI
kaggle datasets download -d dgomonov/new-york-city-airbnb-open-data --unzip
mv AB_NYC_2019.csv data/raw/

# Option B — manual download
# https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data
# Save the CSV to data/raw/AB_NYC_2019.csv
```

### 3. Create your branch

```bash
git checkout -b <your_name>/claude/task_01
```

### 4. Do the task

Open the notebook template: `tasks/task_01_data_ingestion/notebook_template.ipynb`
Read the task spec: `tasks/task_01_data_ingestion/README.md`
Save all outputs to `agents/claude/task_01/outputs/`.

### 5. Score your work

```bash
python tasks/task_01_data_ingestion/evaluate.py \
  --agent agents/claude/task_01/ \
  --name <your_name> \
  --tool "Claude (claude.ai)" \
  --time 25 \
  --notes "clean output, 2 iterations" \
  --failure "none"
```

### 6. Commit and push

```bash
git add agents/claude/task_01/ results/scores.csv
git commit -m "<name>: task_01 claude — score 4/5"
git push -u origin <your_name>/claude/task_01
```

### 7. Open a PR into `main`

Tag a teammate to review. Only merge your own agent folder.

---

## Golden Rules

1. `**data/raw/` is immutable** — never edit it.
2. **Never touch another agent's folder** — `agents/<tool>/` belongs to its owner.
3. **Every task must go through `evaluate.py`** — no hand-editing `scores.csv`.
4. `**SEED = 42` everywhere** — every notebook, every script.
5. **Relative paths only** — no hardcoded absolute paths.
6. **Clear notebook outputs before committing** — Kernel > Restart & Clear Output.
7. **Branch naming: `<name>/<agent>/<task>`** — e.g. `<name>/claude/task_01`.

Full rules: see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Scoring

Each task is worth 5 points. `evaluate.py` runs automated checks then prompts for manual ones. Results accumulate in `results/scores.csv`.


| Task                            | Automated checks                                                                               | Manual checks                             |
| ------------------------------- | ---------------------------------------------------------------------------------------------- | ----------------------------------------- |
| Task 01 — Data Ingestion        | `ingested.csv` present, no missing values, `schema_log.md` present, missingness report present | Assumptions documented                    |
| Task 02 — EDA                   | Notebook present, cells cleared, ≥3 plot files, `eda_summary.md` present                       | No test-set leakage; insights written     |
| Task 03 — Baseline Model        | Output files present, `baseline_results.csv` valid, no absolute paths                          | No data leakage in preprocessing          |
| Task 04 — Improving Performance | `improved_results.csv` with comparison, report present                                         | Improvement is meaningful; no new leakage |


Max total per agent: **20 points**.

### Leakage benchmark

An additional programmatic leakage check runs across all Task 03 and 04 notebooks:

```bash
# From group-coursework/
python tasks/leakage_check.py batch
```

Scores 5 criteria per notebook (Pipeline usage, split-before-fit ordering, no fit on full X, safe target encoding) and appends results to `results/scores.csv` with `task_id = leakage_check_task_0{3,4}`.
