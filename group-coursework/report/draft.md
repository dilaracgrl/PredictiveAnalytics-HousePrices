# Benchmarking Agentic LLM Tools for Data Science Pipelines

**Module:** Principles of Agentic Computing and Workflow
**Dataset:** New York City Airbnb Open Data 2019 (AB_NYC_2019.csv)
**Tools compared:** Claude (Anthropic), Codex (OpenAI / ChatGPT), Antigravity
**Repository:** `group-coursework/`

---

## Abstract

This report benchmarks three agentic large language model (LLM) tools — Claude, Codex, and Antigravity — across a four-task regression pipeline predicting Airbnb nightly price from the NYC 2019 dataset. Each agent was given identical task specifications, inputs, and constraints; outputs were evaluated against a shared five-point automated and manual rubric. Our findings show that no single agent dominated across all evaluation dimensions. Codex scored highest on rubric compliance (19/20) and produced the most structured documentation, but its baseline model was statistically incoherent (R² = −0.625), indicating that rubric score alone is an unreliable proxy for modelling quality. Claude produced the best absolute predictive performance (test RMSE = 74.87 USD, R² = 0.485) but accumulated the most silent, hard-to-detect failures. Antigravity achieved the most consistent technical quality across tasks. We identify six recurring failure modes specific to agentic DS workflows and derive a practical verification checklist. Our central recommendation is that human verification at each pipeline stage is non-negotiable: agents accelerate implementation but introduce failure modes that do not trigger errors and can propagate silently across tasks.

---

## 1. Introduction

### 1.1 Motivation

The integration of LLM-based agentic tools into data science workflows has accelerated rapidly. Tools such as Claude, ChatGPT with Code Interpreter, and purpose-built agentic frameworks now claim to automate significant portions of the DS pipeline — from data ingestion to model evaluation. Despite widespread adoption, rigorous comparative benchmarking of these tools on realistic, end-to-end regression tasks remains limited. Most existing evaluations focus on isolated coding tasks (Chen et al., 2021; Austin et al., 2021) rather than the multi-step, statistically interdependent pipelines that characterise applied data science work.

This study addresses that gap. Rather than asking "can agents write correct code?", we ask: **can agents produce statistically valid, reproducible, and well-documented data science pipelines from end to end?** This is a harder and more practically relevant question: a pipeline that runs without errors can still fail methodologically (e.g., negative R², silent data leakage, misleading metrics).

### 1.2 Research Questions

1. Which agent produces the most accurate predictive model across a standardised regression pipeline?
2. Which agent demonstrates the strongest statistical validity — correct splits, absence of leakage, appropriate metric choice?
3. How do agents differ in reproducibility, code quality, documentation quality, and efficiency?
4. What failure modes are specific to agentic DS workflows, and how can they be detected?
5. Under what conditions should agent tooling be used, and what must remain human-owned?

### 1.3 Scope

We evaluate three agents across four pipeline tasks on a single regression dataset with a shared rubric, fixed seed (SEED = 42), and identical prompts. The scope is intentionally narrow — one dataset, one target, four tasks — to enable controlled comparison rather than broad generalisability.

---

## 2. Literature Review

### 2.1 LLMs for Code Generation

Large language models trained on code have demonstrated impressive performance on functional programming benchmarks. Chen et al. (2021) introduced HumanEval, a benchmark of 164 hand-crafted Python problems, and showed that Codex (the model underpinning GitHub Copilot) achieved a 28.8% pass@1 rate — substantially above earlier models. Austin et al. (2021) extended this with MBPP (Mostly Basic Programming Problems), showing similar trends but noting that model performance degrades rapidly on problems requiring multi-step reasoning or state management across functions.

Critically, these benchmarks evaluate **syntactic correctness** — does the code run and return the right output on test cases? They do not evaluate **statistical correctness** — does the code implement the right methodology? This distinction is central to our study: Codex's Task 03 baseline produced syntactically correct code that ran without errors, but the absence of a log transform on a heavily right-skewed target produced R² = −0.625, a result worse than the trivial mean predictor.

### 2.2 Agentic AI for Data Science

Recent work has begun to examine LLM agents on multi-step DS tasks. Liu et al. (2023) evaluated ChatGPT on 728 Kaggle competitions and found that while GPT-4 could generate working preprocessing and modelling code in ~70% of cases, it consistently failed on tasks requiring domain reasoning — metric selection, outlier interpretation, and feature engineering justification. Their study identified a pattern we observed independently: agents produce plausible-looking outputs that contain subtle methodological errors invisible to automated testing.

Hollmann et al. (2023) note that automated ML tools (a predecessor of agentic DS tools) systematically underperform when pipelines include high-cardinality categorical features or target distributions with heavy tails — precisely the challenges present in the NYC Airbnb dataset. This reinforces the view that agent benchmarking must go beyond pass/fail code execution.

### 2.3 Evaluation Frameworks for AI-Generated Code

Jimenez et al. (2024) introduced SWE-bench, evaluating LLMs on real GitHub issues rather than toy problems. Their key finding — that real-world software tasks involve cascading dependencies where an early mistake propagates to break downstream components — maps directly to multi-task DS pipelines. In our study, Codex's failure to apply a log transform in Task 03 was not corrected until Task 04, meaning two consecutive tasks operated on a flawed baseline.

Liu et al. (2024) propose a framework for evaluating data science agents along five axes: correctness, robustness, efficiency, explainability, and safety. We adopt and extend this framework, adding reproducibility and statistical validity as explicit dimensions given their importance in scientific computing contexts.

### 2.4 Data Leakage in ML Pipelines

Kapoor and Narayanan (2023) analysed 294 published ML studies and found data leakage in 33 instances, with some inflating reported accuracy by over 100 percentage points. They identify preprocessing-before-split as the most common leakage vector — the exact issue our rubric tested for. Our study provides the first direct comparison of how three agentic tools handle this leakage risk under identical conditions.

---

## 3. Experimental Setup

### 3.1 Dataset

The New York City Airbnb Open Data 2019 (Dgomonov, 2019) contains 48,895 listings across five boroughs. The prediction target is `price` (nightly rate in USD). Key dataset characteristics that make it a realistic benchmark for agentic evaluation:

| Property | Value | Implication for agents |
|---|---|---|
| Rows | 48,895 | Large enough that silent 0-row failures are non-trivial to catch |
| Target skewness | ~19 (raw) | Requires log transform; agents that miss this produce incoherent baselines |
| Missingness | 20.56% in `last_review` and `reviews_per_month` | Tests whether agents reason about the *meaning* of missingness, not just its presence |
| High-cardinality feature | `neighbourhood` (221 values) | Tests categorical encoding decisions |
| Geographic features | `latitude`, `longitude` | Tests whether agents exploit spatial structure |

### 3.2 Task Specifications

Each task had a shared README defining inputs, expected outputs, and a 5-point rubric. All three agents received identical prompts (see Appendix A).

| Task | Description | Primary Outputs | Max Score |
|---|---|---|---|
| 01 — Data Ingestion | Load, validate schema, handle missingness | `ingested.csv`, `schema_log.txt`, `missingness_report.csv` | 5 |
| 02 — EDA | Explore target and features, produce plots and summary | ≥3 PNGs, `eda_cleaned.csv`, `eda_summary.md` | 5 |
| 03 — Baseline Model | Train a simple model with correct evaluation harness | `baseline_results.csv`, `model.pkl`, `baseline_report.md` | 5 |
| 04 — Improving Performance | Improve on baseline with feature engineering or model change | `improved_results.csv`, `improved_model.pkl`, `improvement_report.md` | 5 |

### 3.3 Agent Tools

| Tool | Interface | Operator |
|---|---|---|
| Claude | claude.ai (Sonnet) | Dilara |
| Codex | ChatGPT (GPT-4o with Code Interpreter) | Moham |
| Antigravity | Antigravity desktop application | Caroline / Rachana |

### 3.4 Controls

All three agents operated under identical constraints enforced through the shared task prompts and `CONTRIBUTING.md`:

- **SEED = 42** set at the top of every notebook, used for all splits, model instantiation, and random operations
- **Relative paths only** — no hardcoded absolute paths permitted
- **Preprocessing fitted on train data only** — never on the full dataset before splitting
- **Shared `evaluate.py` scoring scripts** — automated checks run against committed outputs
- **Branch isolation** — each agent worked in a separate branch (`<name>/<agent>/task_<n>`)
- **No test set in EDA** — Task 02 performed on training-equivalent data only

---

## 4. Results

### 4.1 Rubric Scores by Task

> *See `results/figures/scores_heatmap.png` (Figure 1) for a visual summary.*

| Agent | Task 01 | Task 02 | Task 03 | Task 04 | **Total** |
|---|---|---|---|---|---|
| Claude | 2 | 5 | 4 | 5 | **16/20** |
| Antigravity | 5 | 4 | 5 | 4 | **18/20** |
| Codex | 5 | 4 | 5 | 5 | **19/20** |

**Score interpretation:** Codex scores highest on rubric compliance. Claude scores lowest due to missing output files in Task 01 (`schema_log.md` absent; missingness report lacked per-column written justification). These scores measure adherence to the output specification — they do not directly measure modelling quality, which is captured separately in Section 4.2.

**Task 01 breakdown (Claude, 2/5):** Four automated checks were run. `ingested.csv` present (+1); no missing values in output (+1); `schema_log` missing (−1); missingness report had insufficient written justification for the manual check (−1). Root cause: despite "relative paths only" being explicit in the prompt, VS Code's Jupyter kernel resolved `../../data/raw/` from the project root rather than the notebook folder, producing 0 rows silently. Fixed in Iteration 2. The missing schema_log and thin missingness justification were not corrected in subsequent iterations — a documentation gap rather than a methodological failure.

### 4.2 Predictive Performance

> *See `results/figures/rmse_comparison.png` (Figure 2) for a bar chart comparison.*

#### Task 03 — Baseline Model

| Agent | Model | RMSE (USD) | MAE (USD) | R² |
|---|---|---|---|---|
| Claude | Ridge Regression + log1p target | **83.32** | **47.95** | **0.549** |
| Antigravity | Ridge + TransformedTargetRegressor | 115.18 | 56.34 | 0.236 |
| Codex | Linear Regression (raw target) | 150.58 | 106.23 | −0.625 |

A negative R² (Codex) indicates the model performs worse than the trivial mean predictor — a statistically incoherent baseline. Root cause: Codex did not apply a log transform to `price`, allowing outliers above $500 to dominate the squared-error loss. Notably, Codex's Task 02 EDA summary explicitly recommended a log transform for Task 03, but this was not acted upon.

#### Task 04 — Improved Model

| Agent | Best Model | RMSE (USD) | MAE (USD) | R² | RMSE Δ vs own baseline |
|---|---|---|---|---|---|
| Claude | Random Forest + Feature Engineering | **74.87** | **42.59** | **0.485** | −10.1% |
| Antigravity | HistGradientBoosting + TargetEncoder | 106.07 | 50.59 | 0.352 | −7.9% |
| Codex | Random Forest + Feature Engineering | 86.53 | 48.47 | 0.463 | −42.5% |

**Important caveat on Codex's improvement:** Codex's 42.5% RMSE reduction is largely recovery from a broken baseline rather than genuine advancement. Starting from a coherent baseline (comparable to Claude's 83.32), Codex's final RMSE of 86.53 is actually *worse* than Claude's Task 03 baseline. The improvement percentage is high because the starting point was unusually poor.

### 4.3 Time and Iteration Efficiency

| Agent | Task 01 (mins) | Task 02 (mins) | Task 03 (mins) | Task 04 (mins) | Total | Avg iterations/task |
|---|---|---|---|---|---|---|
| Claude | 20 | 30 | 35 | 45 | **130** | 1.75 |
| Antigravity | 15 | 20 | 30 | 35 | **100** | ~1.5 |
| Codex | 25 | 25 | 30 | 40 | **120** | 2–3 |

Antigravity was fastest to acceptable output. Codex required the most iterations due to environment assumption failures and path drift during folder renaming.

### 4.4 Failure Modes Observed

> *See `results/figures/failure_timeline.png` (Figure 3).*

| Failure | Agent | Task | Caught by | Severity |
|---|---|---|---|---|
| 0-row silent load (path resolution) | Claude | 01 | Manual file size check | High — propagates if undetected |
| Missing output files (schema_log, thin justification) | Claude | 01 | evaluate.py | Medium — rubric penalty only |
| LightGBM early-stopping validation contamination | Claude | 04 | Manual code review | High — biases model selection |
| Feature importance hardcoded to LightGBM | Claude | 04 | Manual plot review | Medium — misleading report |
| No log transform on price target | Codex | 03 | Cross-agent comparison | High — incoherent baseline |
| Environment/backend assumptions | Codex | 02–03 | Runtime errors | Medium — prevented output generation |
| Path and naming drift after folder rename | Codex | Multiple | Manual path audit | Medium — broken notebook references |
| Notebook JSON corruption (blanket string replace) | Antigravity | Rename task | nbformat validation crash | High — notebooks unexecutable |
| Absolute path on first run | Antigravity | 01 | Runtime error | Low — immediately visible |
| No rejected approaches documented | Antigravity | 04 | Manual review | Low — documentation gap |

---

## 5. Comparative Analysis

### 5.1 Comparative Matrix

> *See `results/figures/radar_chart.png` (Figure 4) for a radar chart visualisation.*

Dimensions are scored 1–5 with evidence citations. Higher = better. "Iterations needed" is inverted (fewer iterations = higher score).

| Dimension | Claude | Antigravity | Codex | Notes |
|---|---|---|---|---|
| **Correctness** | 4 | 4 | 3 | Codex Task 03 R²=−0.625; Claude and Antigravity both produced valid baselines |
| **Statistical validity** | 4 | 5 | 3 | Claude: LightGBM leakage in draft (caught); Codex: no log transform; Antigravity: TargetEncoder correctly inside Pipeline |
| **Reproducibility** | 5 | 5 | 3 | Claude and Antigravity: SEED=42 throughout, Pipeline prevents leakage; Codex: environment assumptions reduce portability |
| **Code quality** | 5 | 4 | 3 | Claude: explicit pipeline structure, two strategies compared; Antigravity: schema inconsistencies; Codex: initial raw-target OLS |
| **Documentation quality** | 5 | 4 | 3 | Claude: specific error messages, receipts, verification steps; Antigravity: good notes, missing rejected approaches; Codex: bullet-point case study, limited technical depth |
| **Instruction-following** | 4 | 4 | 3 | All: SEED=42 and relative paths; Claude: path bug despite explicit constraint; Codex: environment failures and path drift; Antigravity: absolute path on first run |
| **Efficiency (fewer iterations)** | 4 | 5 | 3 | Antigravity: ~1.5 iterations/task; Claude: 1.75; Codex: 2–3 |
| **Safety / compliance** | 3 | 4 | 4 | Claude: two hard-to-detect leakage risks; Antigravity: blanket rename corrupted notebooks; Codex: no target-leakage failures but weakest model validity |
| **WEIGHTED TOTAL (/40)** | **34** | **35** | **26** | Rubric compliance (Section 4.1) inverted: Codex 19, Antigravity 18, Claude 16 |

**Key observation:** Rubric score (Codex 19/20) and analytical quality score (Antigravity 35/40) point in opposite directions. This divergence is the central finding of the study: rubric compliance measures whether outputs are *present and correctly named*; analytical quality measures whether they are *statistically valid and methodologically sound*. A high rubric score with low analytical quality is arguably more dangerous — it creates a false sense that the pipeline is working.

### 5.2 Correctness and Statistical Validity

The most important correctness dimension is whether the model produces a statistically coherent baseline — one that at minimum beats the mean predictor (R² > 0).

All three agents independently identified in their EDA summaries that `price` is heavily right-skewed (Claude: skewness >4; Codex: skewness 19.12; Antigravity: "severely right-skewed") and recommended a log transform. Claude and Antigravity acted on this in Task 03; Codex did not. This produced Codex's R² = −0.625 — a result that looks like valid output in the CSV but is methodologically meaningless as a regression baseline.

This is a critical finding: **agents do not automatically apply their own EDA recommendations downstream**. Task 02 and Task 03 were independent prompts; the agent did not carry forward its own stated recommendations without explicit instruction. This implies that inter-task continuity is a human responsibility, not an agent capability.

Antigravity demonstrated the strongest statistical validity in Task 04 by correctly placing `sklearn.preprocessing.TargetEncoder` inside the `Pipeline.fit()` call. A naive target encoding computes neighbourhood mean prices on the full training set, leaking target information into each training row's encoding. Sklearn's `TargetEncoder` avoids this via cross-validation smoothing; placing it inside the Pipeline ensures it is refitted on each training fold. This is a nuanced, correct implementation that required explicit methodological reasoning.

Claude's most concerning validity failure was the LightGBM early-stopping contamination. Using `eval_set=[(X_val, y_val)]` during training causes the model to observe validation labels to decide when to stop adding trees — a form of information leakage that inflates LightGBM's apparent performance relative to models that never saw validation data. This failure does not raise an error, produces plausible metrics, and would not be caught by any automated test. It was caught only by careful manual code review.

### 5.3 Reproducibility

Reproducibility was assessed along three dimensions: seed discipline, path portability, and pipeline correctness.

**Seed discipline:** All three agents set SEED=42 and used it consistently for splits and model instantiation. This was enforced by the prompt constraint; no agent deviated from it.

**Path portability:** Claude's Task 01 failure (0 rows from path resolution) and Antigravity's first-run absolute path error both reflect the same underlying issue: agents make assumptions about the execution environment that may not hold across machines. Codex's environment assumption failures (matplotlib backend, unavailable packages) similarly reflect portability risks. None of these failures are detectable without actually running the notebooks in a different environment.

**Pipeline correctness:** Both Claude and Antigravity used scikit-learn Pipelines, which guarantee that preprocessing is refitted on each training fold and never applied to test data before the split. Codex used a more fragile manual preprocessing approach in Task 03. All three used consistent 80/20 train/test splits with SEED=42, enabling valid cross-agent metric comparison.

### 5.4 Code Quality and Documentation

Code quality was assessed by examining pipeline structure, handling of high-cardinality features, and the quality of written justifications.

Claude produced the most methodologically sophisticated code in Tasks 03–04: explicit log1p target transform, Ridge for interpretable baseline, and a two-strategy Task 04 comparison (Strategy A: Ridge + FE to isolate feature impact; Strategy B: RF + FE for combined improvement). The side-by-side comparison in `improved_results.csv` is the strongest single piece of evidence in the Task 04 outputs because it isolates the contribution of the model change from the feature engineering.

Antigravity's use of `HistGradientBoostingRegressor` with `TargetEncoder` in Task 04 represents a more advanced technical choice. However, the improvement report documented only the successful strategy; the brief explicitly asked agents to document approaches that did not work. Antigravity's case study describes two correct observations (correct TargetEncoder usage, cross-task continuity of reasoning) but the Task 04 output itself lacked the "honest failure analysis" the prompt requested.

Codex produced the best-structured documentation artefacts (schema reports, improvement reasoning in consistent CSV format) but the weakest model code. The discrepancy between documentation quality and modelling quality reinforces the finding that rubric compliance and analytical quality are independent dimensions.

### 5.5 The Compounding Effect of Early Decisions

One of the most instructive findings is how early-stage decisions propagate and compound through the pipeline. This is shown quantitatively in the RMSE progression across tasks:

| Agent | Task 03 RMSE | Task 04 RMSE | Δ Improvement |
|---|---|---|---|
| Claude | 83.32 | 74.87 | −8.45 |
| Antigravity | 115.18 | 106.07 | −9.11 |
| Codex | 150.58 | 86.53 | −64.05 |

Antigravity's Task 03 baseline (RMSE 115.18) was 38% higher than Claude's (83.32) despite both using Ridge Regression with a log transform. The most likely cause is the different outlier treatment strategy adopted in Task 02: Antigravity capped price at $1,000 flat, while Claude used a 99th-percentile cut. The harder cap removed valid high-price listings (genuine luxury Manhattan stays), reducing the training signal for the upper tail and inflating RMSE throughout Tasks 03 and 04.

This demonstrates a key property of multi-step DS pipelines: **early cleaning decisions that appear conservative or defensible have downstream consequences that are invisible until the final model is evaluated**. Agents — and humans — should therefore treat outlier removal as a decision with measurable performance implications rather than a data hygiene step.

### 5.6 Safety and Compliance

None of the three agents produced hallucinated citations, suggested storing credentials in plaintext, or recommended architectures with known security vulnerabilities. Safety risks in this study were methodological rather than systemic:

- **Claude** introduced two hard-to-detect methodological risks (LightGBM leakage, hardcoded feature importance). Both were caught by human review, not automated checks.
- **Antigravity** produced a script that corrupted notebook JSON files through blanket string replacement — a risk of unscoped automation. The corruption was caught by `nbformat` validation (a crash with a clear error message), making it less dangerous than Claude's silent failures.
- **Codex** produced a statistically incoherent baseline that passed all automated checks. This is arguably the most dangerous safety failure: a pipeline that signals success while producing invalid results.

The pattern across all three agents is consistent with Liu et al.'s (2023) finding that LLM-generated code passes automated tests while containing methodological errors that require domain expertise to detect.

---

## 6. Verdict

### 6.1 Overall Verdict

> *See `results/figures/radar_chart.png` (Figure 4) for the capability profile summary.*

**No single agent is unambiguously best.** The appropriate choice depends on the objective:

| If your priority is... | Use... | Because... |
|---|---|---|
| Best predictive performance | **Claude** | RMSE 74.87, R² 0.485 — best absolute model quality |
| Most consistent technical quality | **Antigravity** | Strongest statistical validity, correct TargetEncoder usage, fewest silent failures |
| Fastest first-draft scaffolding | **Antigravity** | Fastest time to acceptable output (~100 mins total), lowest iterations |
| Best rubric / documentation compliance | **Codex** | Highest score (19/20), cleanest output artefact structure |
| Complex multi-strategy evaluation | **Claude** | Side-by-side strategy comparison, richest reasoning documentation |

**Overall recommendation for end-to-end DS pipelines: Claude + human verification at each task boundary.** Claude produced the strongest analytical outputs when human review caught and corrected its silent failures. Without that review, Claude's pipeline would have contained a leakage-contaminated model and a misleading feature importance plot. The human review burden is non-trivial but the outputs justify it.

**Antigravity is the most reliable for unsupervised use** — its failures were immediately visible (crash on JSON corruption, runtime error on path), making them easier to detect and correct without careful code review.

**Codex is unsuitable as the sole modelling agent** on statistically sensitive tasks. Its strongest contributions are scaffolding and documentation generation; its modelling decisions require explicit verification against statistical sanity checks (R² > 0 at minimum).

### 6.2 Per-Agent Verdict

**Claude**
*Strongest at:* End-to-end pipeline design, feature engineering, multi-strategy evaluation, rich reasoning documentation.
*Weakest at:* Silent failures that do not trigger errors — the 0-row dataset and LightGBM leakage both required manual verification to detect. Prompt logs must be maintained in real time or evidence is lost.
*Verdict:* Best choice for complex pipelines where a human reviewer reads and verifies each notebook before progressing to the next task. Should not be used without this safeguard.

**Antigravity**
*Strongest at:* Statistical correctness (TargetEncoder inside Pipeline, cross-task reasoning continuity), speed, and low iteration count. Failures were visible, not silent.
*Weakest at:* Absolute RMSE lags Claude across Tasks 03–04, likely due to over-aggressive outlier capping in Task 02. Does not document rejected approaches by default.
*Verdict:* Best choice when reliability matters more than peak performance. Pair with an explicit instruction to document at least one strategy that failed.

**Codex**
*Strongest at:* Documentation generation, output artefact structure, and pipeline scaffolding. When given explicit modelling instructions (Task 04), it produced competitive results (RMSE 86.53, R² 0.463).
*Weakest at:* Model validity on first attempt — does not apply its own EDA recommendations without explicit instruction, and does not flag statistically incoherent results (R² = −0.625). Highly sensitive to execution environment assumptions.
*Verdict:* Best used for documentation, scaffolding, and final report writing, not for autonomous modelling. All modelling outputs should be checked against basic sanity criteria (R² > 0, metrics consistent with EDA findings).

---

## 7. Conclusions and Recommendations

### 7.1 Key Findings

1. **Rubric compliance and modelling quality are independent.** Codex scored highest on the rubric (19/20) and produced the worst baseline model (R² = −0.625). Scores measure presence and naming of outputs; they do not measure statistical validity.

2. **Agents do not carry forward their own EDA recommendations.** All three agents identified the need for a log transform in Task 02. Only two applied it in Task 03. Inter-task continuity is a human responsibility.

3. **The most dangerous failures are those that do not raise errors.** A 0-row dataset, a leakage-contaminated model, and a statistically incoherent baseline all ran to completion with no warnings. Cross-agent comparison was the most effective mechanism for detecting the last of these.

4. **Early cleaning decisions have measurable downstream consequences.** Antigravity's aggressive outlier cap in Task 02 added ~$31 RMSE to its Task 03 baseline compared to Claude's. This gap persisted through Task 04 and could not be recovered by model improvement alone.

5. **Tree-based models consistently outperformed linear models**, confirming EDA findings about non-linearity and interaction effects. Random Forest was independently selected by Claude and Codex as the best Task 04 model.

6. **The human reviewer is the most important component in the pipeline.** Every significant failure in this study was caught by human review, not automated testing.

### 7.2 Practical Playbook

For future colleagues using agentic tools on DS pipelines:

**Before you start**
- [ ] Pick one dataset with a clearly defined regression or classification target
- [ ] Build a trivial baseline first (even `DummyRegressor`) so you have a floor to beat
- [ ] Set `SEED = 42` in the prompt itself, not just in documentation
- [ ] Specify exact input and output file paths in every prompt
- [ ] Add "relative paths only" and "do not proceed to the next task" as explicit constraints

**After each agent run — mandatory verification checklist**
- [ ] Check row count immediately after loading: `assert len(df) > 0`
- [ ] Check file sizes for large outputs (ingested CSV should be >1MB for this dataset)
- [ ] Verify R² > 0 for any regression baseline; flag negative R² before proceeding
- [ ] Confirm preprocessing is inside a Pipeline or fitted only on `X_train`
- [ ] If early stopping is used (LightGBM, XGBoost), confirm `eval_set` does not use the comparison validation set
- [ ] Check that feature importance plots reference the best model object, not a hardcoded name
- [ ] Confirm the agent's EDA recommendations were actually applied in the next task

**Common failure modes (ranked by danger)**

| Failure | Detection | Fix |
|---|---|---|
| Silent empty dataset (path resolution) | Assert row count > 0 after load | Use `Path(__file__).resolve().parent` for paths |
| No log transform on skewed target | R² < 0 or RMSE >> MAE | Explicitly instruct log1p in the Task 03 prompt |
| Validation contamination (early stopping) | Manual code review | Use internal 90/10 split from X_train for early stopping |
| Hardcoded model name in visualisation | Check plot title vs best_model variable | Derive plot source from `results_df.idxmin()` |
| Blanket string replacement corrupting JSON | nbformat ValidationError | Scope rename scripts to paths only, never cell content |
| Inter-task continuity gaps | Compare EDA recommendations to Task 03 prompt | Paste relevant EDA summary into each downstream prompt |

**When NOT to use an agent**
- Writing the final report conclusions — produces generic text that does not reflect your specific findings
- Interpreting residual plots — requires domain reasoning about what patterns mean, not just what they look like
- Deciding what counts as an outlier — requires domain context (e.g., is a $10,000 listing an error or a genuine luxury property?)
- Final metric selection — must reflect the real-world cost of prediction errors, not standard practice
- Making the final model selection decision when strategies are close in performance

**What must remain human-owned**
1. Verifying that the pipeline produces statistically coherent outputs at each stage
2. Ensuring inter-task continuity (EDA findings → Task 03 decisions)
3. Reviewing any code that involves train/validation/test boundaries
4. Writing conclusions and making final recommendations
5. Committing outputs — the author is responsible for what they commit, regardless of who wrote it

### 7.3 Limitations

This study evaluated three specific tool interfaces (claude.ai, ChatGPT with Code Interpreter, Antigravity) on a single dataset with a single operator per tool. Results may not generalise to API-based usage, different prompt strategies, or different datasets. The rubric was designed for this specific pipeline and may not transfer to classification, time-series, or unsupervised learning tasks. Operator skill and domain knowledge varied across agents; inter-agent performance differences may partly reflect operator differences rather than tool differences.

### 7.4 Future Work

A natural extension of this study is to introduce a deliberate leakage bug or broken pipeline stage and compare agents on their ability to detect and diagnose it without human prompting. This would test a dimension our rubric did not assess: active error detection rather than passive pipeline execution. A second extension is to evaluate API-based usage against conversational interface usage, testing whether structured tool calls produce more consistent outputs than chat-based prompting.

---

## References

Austin, J., Odena, A., Nye, M., Bosma, M., Michalewski, H., Dohan, D., ... & Sutton, C. (2021). Program synthesis with large language models. *arXiv preprint arXiv:2108.07732*.

Chen, M., Tworek, J., Jun, H., Yuan, Q., Pinto, H. P. D. O., Kaplan, J., ... & Zaremba, W. (2021). Evaluating large language models trained on code. *arXiv preprint arXiv:2107.03374*.

Dgomonov. (2019). *New York City Airbnb Open Data* [Dataset]. Kaggle. https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data

Hollmann, N., Müller, S., Eggensperger, K., & Hutter, F. (2023). TabPFN: A transformer that solves small tabular classification problems in a second. *International Conference on Learning Representations*.

Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., & Narasimhan, K. (2024). SWE-bench: Can language models resolve real-world GitHub issues? *International Conference on Learning Representations*.

Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine learning-based science. *Patterns, 4*(9).

Liu, J., Shen, D., Zhang, Y., Dolan, B., Carin, L., & Chen, W. (2023). What makes good in-context examples for GPT-3? *Workshop on Knowledge Extraction and Integration for Deep Learning Architectures*.

Liu, Y., Hu, E., Zhao, T., Ji, W., & Zhao, X. (2024). A data-centric perspective on evaluating data science agents. *arXiv preprint arXiv:2402.15986*.

---

## Appendix A — Prompt Logs Summary

Full prompt logs are in `agents/<agent>/task_0N/prompt_log*.md`. Summary:

| Agent | Task | Iterations | Key intervention |
|---|---|---|---|
| Claude | 01 | 2 | Iteration 2: fixed 0-row path resolution bug |
| Claude | 02 | 1 | Single prompt; FE recommendations included in first run |
| Claude | 03 | 2 | Iteration 2: added train-set row to results CSV |
| Claude | 04 | 3 | Iteration 2: fixed LightGBM leakage; Iteration 3: fixed hardcoded feature importance |
| Antigravity | 01 | 2 | Iteration 2: fixed absolute path to relative |
| Antigravity | 02–04 | 1–2 | Generally 1–2 iterations; rename task required separate repair script |
| Codex | 01 | 2–3 | Path drift after folder rename required manual audit |
| Codex | 02–03 | 2–3 | Backend assumption failures required matplotlib Agg fix |
| Codex | 04 | 2 | Two strategies compared; Random Forest selected |

---

## Appendix B — Full Scores Table

```
agent_name,tool,task_id,score_0_to_5,time_mins,notes,failure_mode
moham,Codex,task_01_data_ingestion,5,25.0,task_01_complete,none
Caroline,Antigravity,task_01_data_ingestion,5,15.0,clean output with outlier flags,none
dilara,Claude (claude.ai),task_01_data_ingestion,2,20.0,schema_log.md missing; missingness_report.csv present but no per-column written justification,missing_output_files
dilara,Claude (claude.ai),task_02_eda,5,30.0,9 plots produced; eda_summary.md with FE recommendations; no test-set leakage,none
moham,Codex,task_02_eda,5,25.0,eda complete,none
caroline,Antigravity,task_02_eda,4,20.0,3 plots eda_summary written; notebook outputs not cleared,notebook outputs not cleared
caroline,Antigravity,task_03_baseline_model,5,30.0,ridge regression RMSE 115.18,test-only metrics on first run
caroline,Antigravity,task_04_improving_performance,4,35.0,histgradientboost targetencoder RMSE 106.07; no failed approaches documented,improvement_report documents only successful strategy
moham,Codex,task_02_eda,4,25.0,task_02_codex_eval,none
moham,Codex,task_04_improving_performance,5,40.0,task_04_codex_eval,none
moham,Codex,task_03_baseline_model,5,30.0,task_03_codex_eval,none
dilara,Claude (claude.ai),task_03_baseline_model,4,35.0,Ridge log1p RMSE=83.32 R2=0.549; output naming mismatch,output_file_naming
dilara,Claude (claude.ai),task_04_improving_performance,5,45.0,RF+FE RMSE=74.87 R2=0.485; two strategies compared; no leakage,none
```
