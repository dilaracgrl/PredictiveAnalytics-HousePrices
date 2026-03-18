## Tasks Where the Agent Significantly Helped

**1. Scaffolding the entire 5-notebook pipeline structure**

The agent generated the full project architecture in one prompt — folder structure, data loading with column renaming, cleaning pipeline with row-count checkpoints, EDA with 14 professional plots, feature engineering with target encoding, and a 5-model comparison framework. What would have taken me several days of boilerplate coding was produced in hours. I verified each notebook by running it end-to-end and checking outputs matched expectations.

**Receipt:** Interaction log entries 1-6. The agent produced ~153KB of source code across 5 scripts.

**2. Generating the evaluation and error analysis framework**

The agent wrote the bootstrap confidence interval function, multi-seed stability analysis, formal statistical comparison (RF vs LogReg), threshold sweep analysis, subgroup ROC-AUC by airline and hour, and false negative/positive profiling — all in a single interaction. This evaluation code would have been tedious and error-prone to write from scratch.

**Receipt:** Interaction log entries 21-23. Bootstrap CIs, multi-seed evaluation, and formal significance testing were all generated correctly on first attempt.

---

## Tasks Where the Agent Failed

**1. Path resolution bug — produced a silently empty dataset (0 rows)**

The agent wrote notebook 01 with a relative path (`../data/raw/`) that assumed the Jupyter kernel runs from the `notebooks/` folder. VS Code actually sets the kernel working directory to the project root, so the path resolved one level too high, found zero CSVs, and `pd.concat([])` in pandas 2.x silently returns an empty DataFrame. The agent wrote the parquet file with the correct 23-column schema but zero rows (10KB file). This propagated silently downstream — notebook 02 loaded the empty parquet and displayed "0 rows" with no error.

**What made this dangerous:** No error was raised at any point. The pipeline ran successfully end-to-end on an empty dataset. If I hadn't checked the file size and row counts manually, I could have submitted results based on no data.

**How I caught it:** I noticed the parquet file was only 10KB (should be ~60MB) and the notebook output said "Loaded: 0 rows." I checked `ls -lh data/processed/model_dataset.parquet` in the terminal to confirm.

**How I fixed it:** I directed the agent to use CWD-agnostic pathlib resolution and add a FileNotFoundError guard if glob finds zero CSVs.

**Receipt:** Interaction log entries 3-4. Screenshots show the 0-row output and the debugging session.

**2. LightGBM validation contamination — methodologically unfair model comparison**

The agent wrote `lgbm.fit(X_train, y_train, eval_set=[(X_val, y_val)])` for early stopping. This means LightGBM saw the validation labels during training (to decide when to stop adding trees), while Logistic Regression and Random Forest never saw validation data at all. LightGBM therefore had an information advantage in the model comparison — it effectively used the validation set twice (once for tree selection, once for metric comparison).

**What made this dangerous:** The code runs perfectly, produces reasonable-looking metrics, and wouldn't be flagged by any automated test. It's a subtle methodological error that could lead to selecting an inferior model (LightGBM) over a genuinely better one (Random Forest) because of the unfair advantage.

**How I caught it:** While reviewing notebook 04's model training code (interaction log entry 6), I noticed the eval_set parameter referenced X_val/y_val and realised this breaks the assumption that all models are evaluated on the same unseen validation set.

**How I fixed it:** I directed the agent to create an internal 90/10 stratified split from the training data for early stopping, keeping validation completely untouched until final evaluation.

**Receipt:** Interaction log entries 6 and 11. Entry 6 shows I flagged the issue ("Modified — flagged LightGBM early stopping issue"), entry 11 shows the correction.

### 3. Negative R2 on Baseline Model — Model Worse Than the Mean Predictor

**What failed:**
The Codex baseline (Task 03) produced RMSE = 150.58, MAE = 106.23, and R2 = -0.625. A negative R2 means the model performed worse than simply predicting the dataset mean price ($152) for every listing. The code ran without errors and produced a results CSV with plausible-looking numbers.

**What made this dangerous:** There was no automatic signal that anything had gone wrong. The pipeline completed, the CSV was written, and the numbers looked like real metrics. Without comparing R2 against zero or checking against a dummy baseline, this failure would have gone undetected.

**How I caught it:** R2 = -0.625 appeared in `output_03_codex/baseline_results.csv` and was flagged during the evaluate.py run. Cross-referencing against Antigravity (R2 = 0.236) and Claude (R2 = 0.362) on the same dataset confirmed the Codex baseline was not a valid model.

**How I fixed it:** The root cause was the absence of a log transform on the `price` target. The price distribution is heavily right-skewed and extreme values dominated the squared error loss, preventing the linear model from fitting the bulk of the data. Antigravity and Claude both applied `log1p` transforms via `TransformedTargetRegressor`. Task 04 switched to Random Forest, which is more robust to skewed targets without requiring an explicit transform. RMSE improved from 150.58 to 86.53 and R2 from -0.625 to 0.463 — the largest absolute improvement of any agent across all tasks.

**Receipt:** `agents/codex/task_03_codex/output_03_codex/baseline_results.csv` and `agents/codex/task_04_codex/output_04_codex/improved_results.csv`.
---

**Additional agent error (bonus):** The feature importance plot was hardcoded to show LightGBM importances even though Random Forest was the selected best model. The code `'LightGBM-Tuned' if 'LightGBM-Tuned' in models else 'LightGBM'` always picks LightGBM regardless of which model won. I caught this by checking the plot title against the best model name. Receipt: interaction log entry 13.
