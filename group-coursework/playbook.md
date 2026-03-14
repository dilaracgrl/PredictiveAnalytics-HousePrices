# Agentic DS Playbook

> A living document. Add entries as you complete tasks. Entries should be specific and evidence-based — not generic advice. If something surprised you, write it down.

---

## 1. How to Instruct an Agent Effectively

### Principles (fill in as you learn)

- **Be specific about inputs and outputs.** Tell the agent exactly which file to read and exactly what file(s) to produce. Vague instructions produce vague outputs.
- **Specify constraints explicitly.** If you don't want the target column imputed, say so. If you need relative paths, say so. Agents do not infer constraints — they fill gaps with defaults.
- **Provide a worked example format.** Showing the expected structure of an output file (even a 2-row example) cuts iterations significantly.
- **Break tasks into numbered steps.** Agents follow numbered lists more reliably than prose instructions.
- **Include stopping conditions.** Tell the agent when it is done (e.g. "stop after saving the file — do not proceed to modelling").

### Prompt Template

```
Context: <one sentence about the dataset and task>
Input: <exact relative path>
Steps:
1. ...
2. ...
Output: <exact relative path and filename>
Constraints:
- SEED = 42
- Relative paths only
- Do not modify data/raw/
```

### What tends to go wrong (add entries here)

| Issue | Observed with | Fix |
|-------|--------------|-----|
| _(add as you encounter)_ | | |

---

## 2. Repo Setup Checklist

Use this before starting any experimental run.

- [ ] Fresh branch created (`<name>/<agent>/<task>`)
- [ ] `data/raw/` contains the original dataset (unmodified)
- [ ] `requirements.txt` is up to date and tested in a clean venv
- [ ] `SEED = 42` set in all scripts
- [ ] No absolute paths in any file
- [ ] Notebook outputs cleared if committing notebooks
- [ ] `evaluate.py` located and tested with `--help`

---

## 3. Common DS Pitfalls Checklist

Check these in every task before scoring.

### Data Leakage
- [ ] Scaler/encoder fitted only on training data
- [ ] Target variable not used as a feature
- [ ] No future information present in features (time-series context)
- [ ] Train/test split performed before any preprocessing

### Misleading Metrics
- [ ] Metric matches the task type (regression vs classification)
- [ ] Metric not dominated by class imbalance or outliers
- [ ] Baseline (e.g. predicting the mean) always reported alongside model metric
- [ ] R² not used as the only metric (it masks scale)

### Dtype and Schema Issues
- [ ] Numeric columns stored as float/int (not object)
- [ ] Categorical columns consistent (no mixed "Yes"/"yes"/"YES")
- [ ] Date columns parsed as datetime, not string
- [ ] No ID columns accidentally included as features

---

## 4. When NOT to Use an Agent

> Add evidence-based entries as you work through the tasks.

| Situation | Reason | Better approach |
|-----------|--------|-----------------|
| Interpreting residual plots | Agent describes what it sees, not why it matters | Human judgement required |
| Making final metric choice | Agent picks the most commonly cited metric | Requires domain reasoning |
| Deciding what to drop vs impute | Agent makes defensible choices but not domain-aware ones | Human review required |
| Writing the report conclusions | Agent produces plausible but generic text | Original analysis only |
| _(add more as you discover)_ | | |

---

## 5. What Must Remain Human-Owned

These decisions should never be fully delegated to an agent:

1. **Choosing the evaluation metric** — connects to real-world cost of errors; requires domain judgement.
2. **Deciding what counts as a data quality issue** — depends on problem context, not just statistics.
3. **Interpreting error patterns** — requires understanding of what features mean in the real world.
4. **Writing the final conclusions** — must reflect the team's actual findings, not a summary of the prompt.
5. **Committing and reviewing code** — the author is responsible for what they commit, regardless of who (or what) wrote it.

---

## 6. Tool Comparison Table

> Fill in after all tasks are complete.

| Dimension | claude | codex | antigravity |
|-----------|--------|-------|-------------|
| Instruction-following | — | — | — |
| Code quality | — | — | — |
| Documentation quality | — | — | — |
| Iterations needed (avg) | — | — | — |
| Failure modes observed | — | — | — |
| Time to acceptable output (avg mins) | — | — | — |
| Reproducibility out of the box | — | — | — |
| Best suited for | — | — | — |
| Least suited for | — | — | — |
| Overall recommendation | — | — | — |

*Scale: Excellent / Good / Fair / Poor*
