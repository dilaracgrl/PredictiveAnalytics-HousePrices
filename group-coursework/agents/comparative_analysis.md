## 1. Results Summary Table

**Key metric choice**: For modelling tasks (03–04) the key metric is **test RMSE in USD**. MAE and R² are used in notes. For Tasks 01–02 the “metric” is a qualitative assessment of data/EDA quality.


| Agent       | Tool               | Task             | Key metric                         | Score                                                                                                                                        | Time (mins) | Notes                                                                                                                                                                                              |
| ----------- | ------------------ | ---------------- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude      | Claude (Anthropic) | 01 – Ingestion   | Schema & missingness correctness   | Rows=48,895; Cols=16; missingness correctly reported (e.g. `last_review` & `reviews_per_month` both 20.56% missing)                          | N/A         | `schema_log.txt` and `missingness_report.csv` exactly match AB_NYC_2019 spec; flags price=0 and extreme `minimum_nights` but does **not** transform target in Task 01.                             |
| Codex       | OpenAI Codex       | 01 – Ingestion   | Schema & missingness correctness   | Rows=48,895; Cols=16; missingness correctly reported                                                                                         | N/A         | `schema_log.md` and `missingness_report.csv` match Claude’s counts; additionally drops `host_id` and `last_review` at ingestion and clips `minimum_nights` at 99th percentile.                     |
| Antigravity | Antigravity        | 01 – Ingestion   | Schema & missingness correctness   | Rows=48,895; Cols=16; missingness correctly reported                                                                                         | N/A         | `schema_log.md` mirrors same schema; `missingness_report.csv` matches 20.56% for `last_review`/`reviews_per_month`. Outlier strategy similar to Codex (drop price=0, cap extremes) based on notes. |
| Claude      | Claude (Anthropic) | 02 – EDA         | Target understanding & key drivers | Strong right-skew (price up to $10,000); recommends log1p(price); identifies room_type, borough, neighbourhood, lat/long as dominant signals | N/A         | Removes price > 99th percentile and clips `minimum_nights` at 30 for `eda_cleaned.csv`; emphasises Manhattan + entire home/apt as highest-price subgroup.                                          |
| Codex       | OpenAI Codex       | 02 – EDA         | Target understanding & key drivers | Skewness=19.12; 95th=355, 99th=799, 99.5th=1000; recommends log-transform and robust metrics                                                 | N/A         | Confirms room_type and `neighbourhood_group` as strongest; notes spatial gradients; trims price above 99.5th and caps `minimum_nights` at 365 for modelling stability.                             |
| Antigravity | Antigravity        | 02 – EDA         | Target understanding & key drivers | “Severely right-skewed” price; recommends log1p(price); confirms weak linear signal from numeric features                                    | N/A         | Explicitly drops price=0 rows and caps price at $1000; proposes TargetEncoding for `neighbourhood` and spatial clustering on lat/long.                                                             |
| Claude      | Claude (Anthropic) | 03 – Baseline    | **Test RMSE (USD)**                | **83.32** (MAE 47.95; R²_raw 0.362; R²_log 0.5494)                                                                                           | N/A         | Baseline is **Ridge Regression on log1p(price)** with one-hot room_type & borough, numeric features scaled; `neighbourhood` dropped due to high cardinality.                                       |
| Codex       | OpenAI Codex       | 03 – Baseline    | **Test RMSE (USD)**                | **150.58** (MAE 106.23; R² -0.625)                                                                                                           | N/A         | Baseline is **plain Linear Regression on raw price** with standard preprocessing; very poor fit (negative R²) but used as a “floor” to show later gains.                                           |
| Antigravity | Antigravity        | 03 – Baseline    | **Test RMSE (USD)**                | **115.18** (MAE 56.34; R² 0.236)                                                                                                             | N/A         | Baseline is **Ridge Regression** with `TransformedTargetRegressor` using log1p/expm1; better than Codex but weaker than Claude’s Ridge/log baseline.                                               |
| Claude      | Claude (Anthropic) | 04 – Improvement | **Best model RMSE (USD)**          | **74.87** (MAE 42.59; R²_raw 0.485; R²_log 0.647)                                                                                            | N/A         | Compares Baseline Ridge vs **Ridge+FE vs RandomForest+FE**; best is **Random Forest + feature engineering** (target-encoded neighbourhood, geo-clusters, interactions).                            |
| Codex       | OpenAI Codex       | 04 – Improvement | **Best model RMSE (USD)**          | **86.53** (MAE 48.47; R² 0.463)                                                                                                              | N/A         | `strategy_comparison.csv` shows RF vs Gradient Boosting; **Random Forest** best (RMSE 86.53 vs 89.07). Baseline 150.58 → 86.53 (ΔRMSE ≈ -64.0).                                                    |
| Antigravity | Antigravity        | 04 – Improvement | **Best model RMSE (USD)**          | **106.07** (MAE 50.59; R² 0.3521)                                                                                                            | N/A         | Uses **HistGradientBoostingRegressor + TargetEncoder for neighbourhood** and other FE. Improves from RMSE 115.18 → 106.07 but remains weaker than Claude and Codex best models.                    |


---

## 2. What Agents Agreed On

- **Strong right-skew and need for log transformation of `price`**  
  - All three EDA summaries flag `price` as **heavily right-skewed** with extreme tails (e.g. Codex reports skewness 19.12 with max $10,000; Claude and Antigravity use similar language and quantiles).  
  - All three explicitly recommend or implement `**log1p(price)` as the regression target** in modelling: Claude’s baseline is “Ridge Regression on log1p(price)”, Codex’s EDA says “consider log-transform during model training pipeline”, and Antigravity’s baseline uses `TransformedTargetRegressor` with `np.log1p`/`np.expm1`.
- **Location and room type as dominant predictors of price**  
  - Claude: ranks `room_type` and `neighbourhood_group` as top features, noting Manhattan + entire home/apt as the highest-price subgroup and emphasising `neighbourhood` and lat/long as important.  
  - Codex: says “`room_type` is a major signal with clear median-price separation” and that `neighbourhood_group` and spatial coordinates show strong structure.  
  - Antigravity: states that location (`neighbourhood_group`, `neighbourhood`, `latitude`, `longitude`) and `room_type` are the “dominant structural drivers” of price.
- **Structured handling of missingness in `last_review` and `reviews_per_month`**  
  - All agents agree that the ~20.56% missingness in `last_review`/`reviews_per_month` reflects **listings with no reviews**, not random error.  
  - Claude imputes `last_review` as `"No review"` and `reviews_per_month` as 0. Codex drops `last_review` but also imputs `reviews_per_month` as 0. Antigravity’s missingness report shows the same counts and its EDA notes align with the “no reviews → 0” logic. In all cases, there is **no target leakage** from how missingness is handled.
- **Baseline-first, then non-linear model improvement strategy**  
  - Each agent uses a **linear model as the baseline** and then moves to more expressive models in Task 04:  
    - Claude: Ridge/log as baseline → Random Forest with engineered features.  
    - Codex: plain Linear Regression baseline → Random Forest / Gradient Boosting.  
    - Antigravity: Ridge/log baseline → HistGradientBoosting with target encoding.
  - This reflects a shared methodological view: **start simple and interpretable**, then demonstrate performance uplift with trees/ensembles.
- **Standard evaluation metric trio for regression (RMSE, MAE, R²)**  
  - All three report **RMSE** and **MAE** in USD and some form of **R²**.  
  - For Claude, both R² on log and raw scales are included; Codex and Antigravity report R² on raw price.  
  - This consistent trio makes cross-agent comparison straightforward and shows emergent agreement on best-practice reporting for regression.

---

## 3. What Agents Disagreed On

### 3.1 Baseline Model Strength and Target Handling

- **Decision**: What should count as an acceptable **baseline model** for price prediction?  
- **Choices**:  
  - **Claude**: Ridge Regression on **log1p(price)** with reasonable features and regularisation → RMSE **83.32**, R²_raw **0.362**.  
  - **Antigravity**: Ridge Regression with `TransformedTargetRegressor` on log1p(price) → RMSE **115.18**, R² **0.236**.  
  - **Codex**: Plain Linear Regression on **raw price** with the same metric trio → RMSE **150.58**, R² **-0.625**.
- **Which performed better?**  
  - Quantitatively, **Claude’s baseline is much stronger** (RMSE 83 vs 115 vs 151). Codex’s baseline is so weak it underperforms even the naive mean predictor (negative R²).
- **Why did this disagreement occur?**  
  - Claude and Antigravity carried their own EDA insights about skewness directly into the baseline design (log-target, regularised linear model).  
  - Codex treated Task 03 as a purely “minimal baseline” and intentionally accepted a simplistic OLS on raw price to maximise contrast with Task 04, at the cost of a realistic floor.

### 3.2 Outlier and Price-Cap Treatment

- **Decision**: How aggressively to treat **price and `minimum_nights` outliers** before modelling?  
- **Choices**:  
  - **Claude**: For EDA, removes listings **above the 99th percentile of price** and clips `minimum_nights` at 30; price outliers flagged in Task 01 but not removed until later for modelling readiness.  
  - **Codex**: Flags broad IQR-based outliers but keeps high-price outliers in Task 01; in EDA, caps price around 99.5th percentile (~$1000) and clips `minimum_nights` at 365.  
  - **Antigravity**: Drops price ≤0 and caps price at $1000 earlier; `minimum_nights` and other numerics are capped at high percentiles to reduce leverage of extremes.
- **Which performed better?**  
  - It’s hard to attribute performance purely to outlier strategy, but Claude—who removes only the most extreme tail and clips `minimum_nights` more aggressively—ends up with the **best overall RMSE** after improvements. Antigravity, with more aggressive price capping, shows the **weakest final RMSE** (106.07).
- **Why did this disagreement occur?**  
  - Claude tends to preserve as much signal as possible and move heavy-handed cleaning into explicit “modelling readiness” steps.  
  - Codex follows a more traditional robust-stats approach (percentile caps) guided by EDA quantiles.  
  - Antigravity takes a more risk-averse stance toward outliers, possibly over-smoothing extreme but legitimate prices, which can dampen model expressiveness for luxury listings.

### 3.3 Use of High-Cardinality `neighbourhood`

- **Decision**: Whether and how to use `**neighbourhood` (≈221 levels)** in modelling.  
- **Choices**:  
  - **Claude**: Explicitly **excludes `neighbourhood` in the baseline** due to high cardinality, relying instead on borough and geo-features; re-introduces its signal later via **target encoding and geo-clustering** in Task 04.  
  - **Codex**: Signals concern about `neighbourhood`’s cardinality in EDA but keeps it as a one-hot encoded categorical in a generic preprocessing pipeline (no special encoding).  
  - **Antigravity**: Baseline ignores advanced treatment but Task 04 plan explicitly uses `**TargetEncoder` for `neighbourhood`** inside a pipeline.
- **Which performed better?**  
  - **Claude and Codex** both achieve stronger final RMSE than Antigravity, but Claude’s approach (drop in baseline, re-introduce via engineered features with RF) yields the **best** scores overall.  
  - Codex’s simpler one-hot treatment still works well once combined with Random Forest but risks high dimensionality. Antigravity’s TargetEncoder idea is theoretically strong but overall pipeline underperforms.
- **Why did this disagreement occur?**  
  - Differences in how far each agent leans into scikit-learn’s advanced encoders vs basic one-hot; Claude favours interpretable staged complexity, Codex uses standard pipelines, Antigravity uses more niche tools at the expense of simplicity.

### 3.4 Improvement Model Choice

- **Decision**: Which **non-linear model** to choose for Task 04.  
- **Choices**:  
  - **Claude**: Chooses **Random Forest** with carefully designed feature engineering (target-encoded neighbourhood, geo-clusters, interactions).  
  - **Codex**: Benchmarks **Random Forest vs GradientBoostingRegressor** and selects **Random Forest** based on superior RMSE (86.53 vs 89.07).  
  - **Antigravity**: Chooses **HistGradientBoostingRegressor** as the primary upgraded model, with TargetEncoder.
- **Which performed better?**  
  - Empirically, **Random Forest** (Claude and Codex) beats HistGradientBoosting (Antigravity) in this setting: Claude RF+FE RMSE 74.87; Codex RF RMSE 86.53; Antigravity HGBR RMSE 106.07.
- **Why did this disagreement occur?**  
  - Claude and Codex favour more established, robust ensemble defaults and complement them with feature engineering (especially Claude).  
  - Antigravity opts for a more advanced but also more hyperparameter-sensitive algorithm; without extensive tuning and strong baselines, this choice ends up **fragile** in practice.

---

## 4. What Was Robust vs Fragile

### Robust Approaches

- **Log-transforming the target**  
  - Implemented or strongly recommended by all three agents and clearly supported by EDA (skewness ≫ 0, heavy tails).  
  - The agents that actually *used* log1p(price) in baselines (Claude and Antigravity) achieved **substantially better RMSE and R²** than Codex’s raw-price baseline.
- **Location and room-type centric feature space**  
  - All models that performed well rely heavily on **room_type**, **borough**, **neighbourhood**, and **lat/long**.  
  - Even with different encodings, these signals consistently contribute most of the explanatory power, making them **robust core features**.
- **Tree-based models as effective upgrades over linear baselines**  
  - Across agents, moving from linear/log baselines to **Random Forest / Gradient Boosting / HistGradientBoosting** always **reduces RMSE** and increases R².  
  - While quality varies by implementation, the pattern “linear baseline → tree ensemble uplift” is stable and reliable.
- **RMSE + MAE + R² as a reporting bundle**  
  - This trio works robustly across skewed targets: RMSE catches big errors, MAE reflects typical errors, and R² shows explanatory power.  
  - Using all three helps agents (and you) detect pathologies like Codex’s negative R² baseline that RMSE alone might make harder to interpret.

### Fragile Approaches

- **Aggressive price and `minimum_nights` capping**  
  - Antigravity’s strategy of capping price at $1000 and strongly clipping `minimum_nights` appears to **stabilise** training but may **blunt signal** in the upper tail where a lot of price variation lives.  
  - Compared to Claude’s more conservative 99th percentile cut and Codex’s moderate caps, this over-cleaning correlates with weaker final RMSE.
- **Advanced models without proportional validation discipline**  
  - HistGradientBoostingRegressor and LightGBM can be extremely strong, but Claude’s case study shows how **subtle validation contamination** (using `eval_set=(X_val, y_val)` for early stopping) can produce **optimistic but misleading metrics**.  
  - These methods are **fragile** when early-stopping or tuning is not carefully isolated from validation/test labels.
- **Hard-coding assumptions in visualisation and reporting code**  
  - Claude’s feature importance plot was hard-wired to display LightGBM importances even when Random Forest was actually best. This creates a **silent mismatch** between “best model” and “reported importances”.  
  - Any code that assumes a specific model name (e.g. `'LightGBM-Tuned' if ... else 'LightGBM'`) is fragile to legitimate changes in model selection.

---

## 5. Failure Mode Analysis

### 5.1 Empty Dataset Due to Path Resolution Bug (Claude)

- **What happened**  
  - Notebook 01 used a relative path (`../data/raw/`) assuming the kernel’s working directory was `notebooks/`, but VS Code ran the kernel from the project root.  
  - The glob found **zero CSVs**, and `pd.concat([])` silently produced an **empty DataFrame (0 rows)** with the correct schema; downstream notebooks loaded it and “ran fine” but on no data.
- **Why this is dangerous**  
  - There were **no runtime errors**; all later steps executed and produced metrics, but on an empty dataset. This could easily slip into a submission.
- **How it was caught / should be caught**  
  - Manually noticing that the parquet file size was ~10KB instead of ~60MB and that row counts were 0.  
  - Systematic defence: always log **row counts and basic stats after ingestion**, and fail hard if rows == 0 or suspiciously small.

### 5.2 LightGBM Early-Stopping Contamination (Claude)

- **What happened**  
  - For a LightGBM candidate model, the code used `eval_set=[(X_val, y_val)]` during training.  
  - This leaks **validation labels into the training procedure**: LightGBM uses them to choose early-stopping iteration, giving it an unfair advantage over models that never saw validation labels.
- **Impact**  
  - LightGBM’s metrics looked slightly better, potentially leading to its selection over a genuinely better model (Random Forest) under a fair protocol.
- **How it was caught / should be caught**  
  - Careful human review of training code, noticing that `eval_set` used the same validation set reserved for model comparison.  
  - Defensive pattern: use **nested splits** where early stopping uses an internal train/”inner-val” split, leaving the original validation set untouched until final comparison.

### 5.3 Misaligned Feature-Importance Plot (Claude)

- **What happened**  
  - The code for the feature importance plot always selected a LightGBM model (`'LightGBM-Tuned' if 'LightGBM-Tuned' in models else 'LightGBM'`) even when Random Forest was actually chosen as best.
- **Impact**  
  - The report’s “feature importance” section would be **misleading**, describing the LightGBM view of the world while claiming to explain the best model’s behaviour.
- **How it was caught / should be caught**  
  - By manually comparing the plot title / selected model name with the recorded “best model”.  
  - Robust fix: always derive the feature importance source from the **best_model variable**, not from a hard-coded name.

### 5.4 Weak Baseline and Metric Interpretation (Codex)

- **What happened**  
  - Codex’s baseline Linear Regression on raw price produced **RMSE 150.58, MAE 106.23, R² -0.625**, indicating severe underfit.
- **Potential issue**  
  - While not “wrong code”, accepting such a weak baseline without explicitly flagging it as pathological can lead to **overstating the benefits** of Task 04 improvements and mis-calibrated expectations.
- **How to catch / mitigate**  
  - Automatically **check for negative R²** or RMSE worse than a naive mean predictor and treat this as a warning that the baseline may not be meaningful.

### 5.5 Over-aggressive Outlier Trimming (Antigravity)

- **What happened**  
  - Antigravity’s pipeline aggressively drops price=0 listings and caps price at $1000 early; `minimum_nights` and other features are heavily clipped based on percentiles.
- **Risk**  
  - This may **remove valid but rare high-price stays** and long-stay listings, biasing the model towards mid-range prices and hurting performance for extremes.
- **How to catch / mitigate**  
  - Compare distributions **before/after cleaning**, especially of the target, and stress-test models on top percentiles to ensure that cleaning hasn’t collapsed important tails.

*(We did not find clear evidence of hallucinated columns or APIs in the provided artefacts; the main failure modes were subtle methodological errors and overly simplistic baselines.)*

---

## 6. Agent Characterisation

- **Claude (Anthropic)**  
  - Strongest at **end-to-end pipeline scaffolding** and rich methodological reasoning: it sets up multi-notebook workflows, sound EDA, log-target baselines, and coherent feature-engineering plus RF improvements.  
  - Its main weaknesses are **subtle but serious methodological bugs** (path assumptions, validation leakage, hard-coded plotting logic) that don’t throw errors but undermine results if not manually audited.
- **Codex (OpenAI)**  
  - Excels at **straightforward, standard scikit-learn pipelines** and clear metric reporting, and at systematically comparing multiple strategies (e.g. RF vs Gradient Boosting) using concise CSV outputs.  
  - It tends to accept **very weak baselines** (negative R²) and keep modelling choices relatively simple, which is easy to understand but makes strong results heavily dependent on Task-04 upgrades.
- **Antigravity**  
  - Leans into **more advanced models and encoders** (HistGradientBoostingRegressor, TargetEncoder) and shows good awareness of leakage risks in target encoding and complex ensembles.  
  - However, its combination of aggressive cleaning and complex models leads to **more fragile performance**: improvements over baseline are modest, and its final RMSE lags behind Claude and Codex.

---

## 7. Key Insights for the Playbook (Checklist)

- **Always confirm row counts after ingestion.** Log the number of rows/columns and basic stats after reading raw data; fail fast if you see 0 rows or a suspicious file size (Claude’s empty-dataset bug).  
- **Treat `price` as a log-target by default.** For heavily skewed targets like Airbnb prices, implement `log1p(price)` in your baseline model via either manual transforms or `TransformedTargetRegressor`.  
- **Use a simple but *realistic* baseline.** Choose a log-linear model with sensible features (Ridge/log) rather than an obviously underfitting OLS on raw price; check R² and compare against a naive mean predictor.  
- **Standardise evaluation metrics across experiments.** Always report RMSE, MAE, and R² on the same test split so you can compare baselines and improved models across agents or runs.  
- **Handle high-cardinality location features carefully.** Avoid naive one-hot for `neighbourhood`; instead, use target encoding, clustering, or drop it in the baseline and re-introduce later with more advanced models.  
- **Be paranoid about leakage in advanced models.** For early-stopping and encoders, ensure that any use of labels or target statistics is confined to **train-only splits**, with separate untouched validation/test sets.  
- **Avoid over-aggressive outlier capping on the target.** Limit yourself to trimming only the most extreme outliers (e.g. >99th or 99.5th percentile) and inspect before/after distributions to avoid erasing real high-price signal.  
- **Keep reporting and visualisations tied to the actual best model.** Derive feature importance plots and summaries from the selected `best_model` object rather than hard-coding specific algorithm names.

