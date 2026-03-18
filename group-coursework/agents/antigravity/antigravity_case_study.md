# Antigravity Agent Case Study

## Where the Agent Significantly Helped

### 1. Advanced Feature Engineering and Model Selection (Task 04)

**What happened:**
The agent identified that the Ridge baseline (RMSE = 115.18, R2 = 0.236) was underfitting because it could not encode the `neighbourhood` column  221 distinct values make one-hot encoding impractical for Ridge due to multicollinearity and sparsity. The agent proposed switching to `HistGradientBoostingRegressor` with `TargetEncoder` on `neighbourhood`, reasoning that gradient-boosted trees partition on encoded values directly and handle high-cardinality categoricals without the sparsity problem.

The critical methodological step was placing `TargetEncoder` inside the sklearn `Pipeline` `fit()` call rather than applying it before the split. A naive target encoding computes neighbourhood mean prices on the full training set, which leaks target information into each training row's own encoding. Sklearn's `TargetEncoder` avoids this using cross-validation smoothing: each fold's encoding is computed from out-of-fold rows only.

**Receipt and verification:**
The improved model achieved RMSE = 106.07, MAE = 50.59, R2 = 0.352 on the test set  a 7.91% RMSE reduction and 49% relative R2 improvement over baseline. Verification confirmed `TargetEncoder` appeared inside the Pipeline `fit()` call, not before the split. The improved model was loaded from `outputs/improved_model.pkl` and test predictions were manually recomputed to confirm the reported metrics matched. Completed in one iteration in 35 minutes.

**What made this significant:**
The agent produced cross-task continuity: the Task 04 model choice directly responded to the Task 02 EDA finding that categorical location features dominate price prediction and the Task 03 limitation note that Ridge cannot capture spatial interactions. This is not typical of agents that treat each prompt as an isolated request.

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
