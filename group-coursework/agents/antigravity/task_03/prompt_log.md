# Prompt Log: Task 03 - Baseline Model Training

> Paste each prompt you sent to the agent here, in order. Note what changed between iterations.

## Prompt Received
**Prompt:**
```
Prompt 3:
You are helping with a data science coursework project.
The dataset is the New York City Airbnb Open Data (2019).
Your input:    ../task_02/outputs/eda_cleaned.csv
EDA findings:  ../task_02/outputs/eda_summary.md
Project goal:  predict Airbnb nightly listing price (regression on price).

Your job is Task 03: Baseline Model Training and Evaluation Harness.
Work entirely inside this notebook. Save all outputs to outputs/.

SEED = 42  <- set at the top, use for the split, the model, and anything random

... (details omitted for brevity) ...

1. Reason about your model choice BEFORE writing any modelling code
2. Set up a sound train/test split
3. Build a preprocessing pipeline
4. Train your baseline model
5. Evaluate rigorously (RMSE, MAE, R², Diagnostic Plots)
6. Save everything needed for Task 04 to build on
```

## Decisions and Implementation Details
Task 03 implemented the foundational evaluation harness with absolutely enforced isolation bounding to prevent Train/Test leakage.

1. **Model Selection Rationale**:
   - Given the categorical dependency learned in EDA (neighbourhood groups, room types), a linear paradigm relies on converting strings to One-Hot Encoded bits stringing tens or hundreds of columns together.
   - **Decision:** **Ridge Regression**. A standard OLS Linear Regression fails under high multicollinearity, but the Ridge mathematically stabilizes OHE sparse matrices natively through L2 regularization penalty.
   
2. **Train/Test Splitting**:
   - Splitted 80/20 rigidly fixed on `SEED=42`. All processing dimensions from this threshold onward inherently restricted `.fit()` procedures exclusively matching `X_train`.

3. **Preprocessing Scikit-Learn Pipeline**:
   - Constructed an impenetrable Scikit-Learn `Pipeline`.
   - **Transformations:** `StandardScaler` scaled variance on `numeric_cols` restricting fitting mechanics strictly to the 80% train fold. `OneHotEncoder(handle_unknown='ignore')` safely wrapped the low-cardinality nominals.
   - **Log Target Handling:** Ridge Regression was encapsulated within `TransformedTargetRegressor(func=np.log1p, inverse_func=np.expm1)`. This satisfied the requirement discovered in EDA (skew handling) flawlessly while allowing the evaluation phase to score metrics directly mathematically mapped backwards into the absolute USD `price` scale.

4. **Rigorous Evaluation**:
   - Calculated exact test fold prediction scores against Mean Absolute Error (MAE), Root Mean Squared Error (RMSE) and $R^2$. 
   - A scatter diagnostic plot (`plot_actual_vs_predicted.png`) revealed the baseline cleanly capturing macro price dynamics but heavily underpredicting ultra-luxury strata boundaries (as Ridge flattens spatial variance too broadly).

**Output:** `baseline_results.csv` and serialized `model.pkl` pipeline safely isolated to `outputs/`.
