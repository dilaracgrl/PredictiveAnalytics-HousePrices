# Antigravity Agent Case Study

## Where the Agent Significantly Helped

### 1. Advanced Feature Engineering and Model Selection (Task 04)
**What happened:** The agent successfully reasoned about the baseline model's weaknesses (Ridge regression) and proposed a high-impact strategy. It suggested using `HistGradientBoostingRegressor` and explicitly handling the high-cardinality `neighbourhood` feature using `TargetEncoder`. It correctly set up the Scikit-Learn pipeline to ensure target encoding was fitted properly without data leakage.
**Receipts & Verification:** 
The agent generated `improvement_reasoning.md` which accurately documented its assumptions: 
> *"Gradient boosting trees can branch inherently to create multi-dimensional geographic bounding boxes... TargetEncoder explicitly fitted within our Pipeline successfully guarantees that `X_test` remains untainted."*
The code executed cleanly, and the reported evaluation metrics proved the reasoning was sound.

### 2. Systematic Data Profiling and EDA Generation (Tasks 01 & 02)
**What happened:** The agent wrote structured, reusable code to identify missingness and flag outliers, compiling the findings into well-formatted CSV and Markdown reports. It significantly sped up the data auditing phase by automating standard exploratory data analysis logic.

---

## Where the Agent Failed

### 1. Indiscriminate String Replacement Corrupted Notebooks (File Renaming Task)
**What happened:** When asked to rename all files and folders to include an `_antigravity` suffix to prevent merge conflicts, the agent wrote a Python script that performed blanket regex string replacements across all project files. This caused it to inadvertently replace system keys inside the raw Jupyter Notebook JSON (changing `"outputs": []` to `"outputs_antigravity": []`).
**Receipts & Verification:**
When trying to computationally execute the notebooks to verify they still worked, it led to a fatal validation crash:
```python
nbformat.validator.NotebookValidationError: 'outputs' is a required property
Failed validating 'required' in code_cell:
On instance['cells'][1]...
```
**Fix:** The agent had to be instructed to write a new Python script to parse the files and specifically revert `"outputs_antigravity":` back to `"outputs":` to restore the corrupted notebook JSON structures.

### 2. File Locking Issues with Automated Refactoring
**What happened:** During the same renaming task, the agent attempted to rename the `task_04` directory while files from inside that directory were still open in the user's IDE. 
**Receipts & Verification:**
*Log output:*
```
[WinError 32] The process cannot access the file because it is being used by another process: ... 'task_04'
```
**Fix:** The agent had to halt execution and prompt the user to manually close the open tabs in VS Code before the directory could be safely renamed by the OS.
