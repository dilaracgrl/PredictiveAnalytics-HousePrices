# Agentic DS Playbook

> A living document. Entries are specific and evidence-based, drawn from running Antigravity, Claude, and Codex across four standardised data science tasks on the NYC Airbnb 2019 dataset.

---

## 1. How to Instruct an Agent Effectively

### Principles

- **Be specific about inputs and outputs.** Tell the agent exactly which file to read and exactly what file(s) to produce. Vague instructions produce vague outputs. Antigravity produced the correct ingestion outputs in one prompt when given exact filenames; a vague prompt produced an absolute path that broke on every other machine.
- **Specify constraints explicitly.** If you need relative paths, say so. If the target column must not be transformed yet, say so. Agents do not infer constraints; they fill gaps with defaults that may be wrong for your setup.
- **Provide a worked example format.** Showing the expected structure of an output file (even a 2-row example) cuts iterations significantly and prevents schema drift across tasks.
- **Break tasks into numbered steps.** Agents follow numbered lists more reliably than prose instructions. A single paragraph prompt produced more failures than a five-step numbered prompt.
- **Include stopping conditions.** Tell the agent when it is done (e.g. "stop after saving the file, do not proceed to modelling"). Without this, agents continue into the next task and introduce scope creep.
- **Always state SEED = 42 in the prompt itself.** Documenting it only in the report is not sufficient; it must appear in the code cells controlling the split and model instantiation.

### Prompt Template

```
Context: <one sentence about the dataset and task>
Input: <exact relative path from repo root>
Steps:
1. ...
2. ...
Output: <exact relative path and filename>
Constraints:
- SEED = 42
- Relative paths only
- Do not modify data/raw/
- Do not split train/test until instructed
```

### What tends to go wrong

| Issue | Observed with | Fix |
|-------|--------------|-----|
| Absolute paths hardcoded to local machine | Antigravity (Task 01, first attempt) | Add "relative paths only" as an explicit constraint in every prompt that writes to disk |
| No log transform on skewed target variable | Codex (Task 03), caused R2 = -0.625 | Specify target transform explicitly; never assume the agent will apply log1p |
| Notebook JSON corrupted during file rename | Antigravity (rename task), "outputs" key replaced with "outputs_antigravity" | Never use blanket string replacement across all files; scope rename scripts to paths only |
| EDA computed on full dataset before split | Risk flagged in Antigravity Task 02 | State "split train/test FIRST before any analysis" as step 1 in every EDA prompt |
| LightGBM validation contamination | Claude (Task 04), eval_set used validation labels during training | State explicitly that all models must be trained without access to validation labels |
| Silent empty dataset with no error | Claude (Task 01), path resolved one level too high producing 0 rows | Add a row count assertion immediately after loading: assert len(df) > 0 |
| Output schema inconsistent across tasks | Antigravity (Tasks 03 and 04 used different column names) | Provide exact column names in the prompt; include a 2-row example CSV |
| Improvement report documents only successes | Antigravity (Task 04) | Explicitly require: "document at least one approach that did not work and why" |

---

## 2. Repo Setup Checklist

Use this before starting any experimental run.

- [x] Fresh branch created (`<n>/<agent>/<task>`)
- [x] `data/raw/` contains the original dataset (unmodified)
- [x] `requirements.txt` is up to date and tested in a clean environment
- [x] `SEED = 42` set in all scripts and visible in code cells
- [x] No absolute paths in any file
- [x] Notebook outputs cleared before committing (Kernel > Restart and Clear Output)
- [x] `evaluate.py` located and tested with `--help`
- [x] Train/test split performed before any EDA or preprocessing
- [x] All scalers and encoders fitted on training data only

---

## 3. Common DS Pitfalls Checklist

Check these in every task before scoring.

### Data Leakage
- [x] Scaler/encoder fitted only on training data
- [x] Target variable not used as a feature
- [x] No future information present in features (time-series context)
- [x] Train/test split performed before any preprocessing or summary statistics
- [x] Target encoding uses cross-validation smoothing or out-of-fold computation, not full-dataset means

### Misleading Metrics
- [x] Metric matches the task type (regression vs classification)
- [x] R2 checked against zero; a negative R2 means the model is worse than predicting the mean
- [x] Baseline (predicting the mean) always reported alongside model metrics
- [x] At least two metrics reported (e.g. RMSE and R2); a single metric masks model behaviour
- [x] Log-transformed target metrics (R2_log) reported separately from raw-scale metrics (R2_raw)

### Dtype and Schema Issues
- [x] Numeric columns stored as float/int (not object)
- [x] Categorical columns consistent (no mixed "Yes"/"yes"/"YES")
- [x] Date columns parsed as datetime, not string
- [x] No ID columns accidentally included as features
- [x] Output CSV column names match the agreed schema across all agents and tasks

---

## 4. When NOT to Use an Agent

Evidence-based entries drawn from this benchmarking exercise.

| Situation | Reason | Better approach |
|-----------|--------|-----------------|
| Interpreting residual plots | Agent describes what it sees visually, not what it means for model fit or next steps | Human judgement required |
| Making final metric choice | Agent picks the most commonly cited metric, not the one that best reflects the real-world cost of errors | Requires domain reasoning |
| Deciding what to drop vs impute | Agent makes statistically defensible choices but cannot assess domain context (e.g. whether zero reviews means a new listing or an inactive one) | Human review required |
| Writing the report conclusions | Agent produces plausible but generic text that does not reflect the team's specific findings | Original analysis only |
| Renaming files and folders during refactor | Blanket string replacement corrupts non-path strings in JSON files such as notebook cell keys | Write targeted rename scripts with explicit path-only scope |
| Checking whether a model beats the mean predictor | Agent reports metrics without flagging negative R2 as a modelling failure | Always compare against a DummyRegressor or mean baseline explicitly |
| Documenting rejected approaches | Agent reports only the successful strategy by default | Explicitly instruct: "document what you tried that did not work" |

---

## 5. What Must Remain Human-Owned

These decisions should never be fully delegated to an agent.

1. **Choosing the evaluation metric.** Connects to the real-world cost of prediction errors; requires domain judgement that agents do not have.
2. **Deciding what counts as a data quality issue.** Depends on problem context, not just statistics. A missing review frequency may mean a new listing or an inactive one; only domain knowledge distinguishes these.
3. **Interpreting error patterns.** Requires understanding what features mean in the real world, not just their correlation structure.
4. **Writing the final conclusions.** Must reflect the team's actual findings, not a summary of the prompt or a generic pattern from training data.
5. **Committing and reviewing code.** The author is responsible for what they commit regardless of who wrote it. Silent failures (0-row datasets, negative R2) require human verification at each stage.
6. **Verifying leakage boundaries.** Automated checks catch obvious cases; subtle leakage such as LightGBM using validation labels for early stopping requires manual notebook inspection.

---

## 6. Tool Comparison Table

Populated from evaluate.py scores, committed output files, and case study evidence across all four tasks on the NYC Airbnb 2019 dataset.

| Dimension | Claude | Codex | Antigravity |
|-----------|--------|-------|-------------|
| Instruction-following | Good: followed task specs precisely; path resolution bug on Task 01 required one fix | Fair: environment assumptions and path drift caused failures across multiple tasks, requiring 2 to 3 iterations per task | Good: followed specs consistently; absolute path on Task 01 first run, fixed with explicit constraint |
| Code quality | Excellent: log1p transform applied, Pipeline structure correct, two improvement strategies compared with evidence | Poor initially: no log transform on price caused R2 = -0.625 on baseline; Task 04 switch to Random Forest corrected this | Good: TargetEncoder correctly inside Pipeline fit(); schema inconsistencies across task outputs |
| Documentation quality | Excellent: case study documents specific error messages, failure mechanisms, and verification steps with exact receipts | Fair: case study uses bullet points with limited technical depth; prompt logs fully populated across all tasks | Good: notes.md contains cross-agent comparison and per-task failure diagnosis; improvement report missing rejected approaches |
| Iterations needed (avg) | 1 to 2 per task | 2 to 3 per task | 1 to 2 per task |
| Failure modes observed | Silent 0-row dataset (no error raised); LightGBM validation contamination giving unfair model comparison advantage | R2 = -0.625 baseline (worse than mean predictor); backend environment assumptions; path drift after folder rename | Absolute path on first run; notebook JSON corruption during rename; no rejected approaches documented in Task 04 |
| Time to acceptable output (avg mins) | 35 | 30 | 25 |
| Reproducibility | High: SEED=42 in code and report, Pipeline prevents leakage, train/val/test metrics all reported | Medium: baseline failure suggests environment sensitivity; Task 04 correct and reproducible | High: SEED=42 throughout, Pipeline structure verified, relative paths enforced |
| Best suited for | Complex end-to-end pipelines requiring feature engineering, multi-strategy comparison, and detailed evaluation harnesses | Fast initial scaffolding and documentation generation where a human will verify outputs before use | Structured ingestion and baseline tasks with clearly defined output schemas and file names |
| Least suited for | Tasks where prompt logs must be captured in real time; empty logs undermine benchmarking evidence | Tasks requiring statistical correctness on first attempt without human verification of model assumptions | Tasks requiring a documented decision trail of rejected approaches and multi-split evaluation |
| Overall recommendation | Strongest for end-to-end modelling pipelines; always verify path resolution and validation design before accepting results | Use for scaffolding only; treat first-attempt model outputs as drafts requiring human review of assumptions | Reliable accelerator for ingestion and baseline tasks; pair with explicit schema constraints and human-authored improvement reports |

*Scores from evaluate.py: Claude Task 01 2/5, Task 02 5/5 | Codex Task 01 5/5, Task 02 4/5, Task 03 5/5, Task 04 5/5 | Antigravity Task 01 5/5, Task 02 4/5, Task 03 5/5, Task 04 4/5*
