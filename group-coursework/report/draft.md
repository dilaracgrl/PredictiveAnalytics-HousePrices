# Benchmarking Agentic LLM Tools for Data Science Coursework

**Module:** [Module Name]
**Team:** [Team Name / Number]
**Date:** [Submission Date]
**Dataset:** [Dataset Name]
**Tools compared:** Claude, Codex, Antigravity

---

## Abstract

<!-- 150–200 words. State the research question, methodology, key findings, and main recommendation. Write last. -->

---

## 1. Introduction

<!--
- Motivation: why benchmark agentic LLM tools for DS tasks?
- Research question: which tool produces the most accurate, reproducible, and well-documented outputs on standardised DS tasks?
- Scope: four pipeline tasks (data ingestion, EDA, baseline model, improving performance), one dataset, three tools, evaluated against a shared rubric.
- Structure of the report.
-->

---

## 2. Literature Review

<!--
- Prior work on LLMs for code generation (cite 3–5 papers)
- Prior work on agentic AI for data science pipelines
- Evaluation frameworks for AI-generated code
- Gaps this study addresses
-->

---

## 3. Experimental Setup

### 3.1 Dataset

<!-- Describe the dataset: source, size, features, target variable, known quality issues. -->

### 3.2 Tasks

| Task | Description | Primary output |
|------|-------------|----------------|
| Task 01 | Data Ingestion | `ingested.csv`, `schema_log.md`, `missingness_report.md` |
| Task 02 | EDA | plot PNGs, `eda_summary.md` |
| Task 03 | Baseline Model | `baseline_results.csv`, `model.pkl` |
| Task 04 | Improving Performance | `improved_results.csv`, `improved_model.pkl` |

### 3.3 Tools

| Tool | Version / Access | Interface used |
|------|-----------------|----------------|
| Claude | [version] | [claude.ai / API] |
| Codex | [version] | [ChatGPT / API] |
| Antigravity | [version] | [interface] |

### 3.4 Scoring Rubric

<!-- Summarise the 5-point rubric (automated checks + manual checks). Reference evaluate.py. -->

### 3.5 Controls

<!-- SEED = 42, relative paths, shared evaluate.py, branch isolation — explain why these controls matter. -->

---

## 4. Results

### 4.1 Scores by Task

<!-- Insert or reference results/scores.csv. Summarise as a table. -->

| Agent | Task 01 | Task 02 | Task 03 | Task 04 | Total |
|-------|---------|---------|---------|---------|-------|
| Claude | — | — | — | — | — |
| Codex | — | — | — | — | — |
| Antigravity | — | — | — | — | — |

### 4.2 Time Taken

<!-- Bar chart or table of time_mins per agent per task. Reference results/figures/. -->

### 4.3 Failure Modes Observed

<!-- Summarise the failure_mode column from scores.csv. Group by tool. -->

---

## 5. Comparative Analysis

### 5.1 Instruction-Following

<!-- Which tool required fewest iterations? What prompting strategies worked? -->

### 5.2 Code Quality and Correctness

<!-- Accuracy of outputs, presence of bugs, correctness of logic. -->

### 5.3 Documentation Quality

<!-- Quality of generated markdown reports, comments, explanations. -->

### 5.4 Reproducibility

<!-- Did re-running each agent's notebooks from scratch produce identical outputs? Observations from task_03 and task_04. -->

### 5.5 Overall Strengths and Weaknesses

<!-- Reference playbook.md § 6 tool comparison table. -->

---

## 6. Conclusions and Recommendations

<!--
- Which tool performed best overall, and on which tasks?
- Under what conditions would you recommend each tool?
- What should remain human-owned regardless of tool choice?
- Limitations of this study.
- Future work.
-->

---

## References

<!-- APA or IEEE format. See report/references.bib for BibTeX entries. -->

---

## Appendix A — Prompt Logs

<!-- Summary of prompts used per agent per task. Full logs in agents/*/logs/. -->

| Agent | Task | Final prompt (truncated) | Iterations |
|-------|------|--------------------------|------------|
| Claude | Task 01 | | |
| Codex | Task 01 | | |
| Antigravity | Task 01 | | |

*(continue for all tasks)*

---

## Appendix B — Full Scores Table

<!-- Paste or embed results/scores.csv here in full. -->

```
agent_name,tool,task_id,score_0_to_5,time_mins,notes,failure_mode
(paste CSV contents here)
```
