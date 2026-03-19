# Agent Benchmarking Report — NYC Airbnb Price Prediction

**Dataset:** AB_NYC_2019.csv — 48,895 listings, target: `price` (USD, regression)
**Agents:** Claude (Dilara) · Codex (Moham) · Antigravity (Caroline / Rachana)
**Tasks:** 01 Data Ingestion · 02 EDA · 03 Baseline Model · 04 Improving Performance

---

## Scorecard

| Agent | Task 01 /5 | Task 02 /5 | Task 03 /5 | Task 04 /5 | **Total /20** |
|---|---|---|---|---|---|
| **Claude** | 2 | 5 | 4 | 5 | **16** |
| **Antigravity** | 5 | 4 | 5 | 4 | **18** |
| **Codex** | 5 | 4 | 5 | 5 | **19** |

> ⚠️ Rubric score ≠ model quality. Codex scored 19/20 but produced R² = −0.625 on its baseline — worse than predicting the mean. See Task 03 for the full breakdown.

---

## Comparative Matrix

| Dimension | Claude | Antigravity | Codex |
|---|---|---|---|
| **Output files complete** | ✗ schema_log missing Task 01 | ✓ all files present | ✓ all files present |
| **Log transform on target** | ✓ log1p applied | ✓ TransformedTargetRegressor | ✗ raw price — caused R²=−0.625 |
| **Preprocessing — train only** | ✓ Pipeline | ✓ Pipeline | ✓ Pipeline (Task 04 only) |
| **SEED = 42 enforced** | ✓ | ✓ | ✓ |
| **Relative paths** | ✗ first run (0-row bug) | ✗ first run (absolute path) | ✗ path drift after rename |
| **Baseline R²** | 0.549 | 0.236 | −0.625 |
| **Best model R²** | **0.485** | 0.352 | 0.463 |
| **Best RMSE (USD)** | **74.87** | 106.07 | 86.53 |
| **Neighbourhood handling** | Target encoding + geo-cluster | TargetEncoder in Pipeline | One-hot |
| **Failure type** | Silent (no error raised) | Visible (crash / runtime error) | Visible but misleading (R² < 0 with no warning) |
| **Iterations needed** | 1.75 avg | ~1.5 avg | 2–3 avg |
| **Time to completion** | 130 mins | **100 mins** | 120 mins |

---

## Task 01 — Data Ingestion

### What each agent was asked to do
Load `AB_NYC_2019.csv`, validate the schema, handle missingness, flag outliers, save `ingested.csv` + `schema_log` + `missingness_report`.

### Task 01 — At a glance

| Agent | Schema log | Missingness report | Outlier flags | Rows out | Path handling | Score |
|-------|------------|--------------------|---------------|----------|---------------|-------|
| **Claude** | `schema_log.txt` (wrong extension for rubric) | CSV, no per-column justification | price=0 dropped, >$500 flagged | 48,884 (11 dropped) | ✗ First run: 0 rows (path bug) | 2/5 |
| **Antigravity** | `schema_log.md` | CSV + handling strategy in markdown | price=0 dropped, price cap $1000 | Capped | ✗ First run: absolute path (fixed) | 5/5 |
| **Codex** | `schema_log.md` + description column | CSV with **handling_strategy** and **justification** per column | IQR + rule-based; clip `minimum_nights` 99th | Dropped price≤0, clipped numerics | ✗ Path drift after rename | 5/5 |

### Missingness in the dataset

| Column | Missing | % | Meaning |
|---|---|---|---|
| `last_review` | 10,052 | 20.56% | Never reviewed — not a data error |
| `reviews_per_month` | 10,052 | 20.56% | Never reviewed — semantically zero |
| `host_name` | 21 | 0.04% | Negligible |
| `name` | 16 | 0.03% | Negligible |

### How each agent handled it

**Claude** — Filled `reviews_per_month` with 0 (semantically correct), documented in `missingness_report.csv`. Produced `schema_log.txt` and `outlier_flags.txt`. **Score: 2/5** — the missingness report had no per-column written justification for each decision, and the automated check for `schema_log.md` failed (Claude saved `.txt` not `.md`).

> **Critical failure:** Despite "relative paths only" being explicit in the prompt, the path `../../data/raw/AB_NYC_2019.csv` resolved incorrectly in VS Code (kernel runs from project root, not notebook folder). `pd.concat([])` returned an empty DataFrame — **0 rows, no error raised**. Caught only by manually checking file size (~10KB vs expected ~60MB). Fixed in Iteration 2 with a `FileNotFoundError` guard.

**Antigravity** — Produced `schema_log.md`, `missingness_report.csv`, and `outlier_flags.txt` cleanly. Dropped `price = 0` rows and capped `price` at $1,000. Flagged outliers in numeric columns. **Score: 5/5**. First run used an absolute path — fixed immediately (visible error, easy to catch).

**Codex** — Most detailed missingness report: structured CSV with `column`, `missing_count`, `missing_pct`, `handling_strategy`, and `justification` per column. Also dropped `host_id` (identifier, not predictive) and clipped `minimum_nights` at 99th percentile at ingestion. **Score: 5/5**.

### Code comparison — missingness handling

| Decision | Claude | Antigravity | Codex |
|---|---|---|---|
| `reviews_per_month` NaN | Fill with 0 | Fill with 0 | Fill with 0 |
| `last_review` NaN | Documented | Documented | **Dropped** (high missingness, date-type) |
| `host_id` | Kept | Kept | **Dropped** (identifier, not a feature) |
| `price = 0` rows | Not dropped | **Dropped** | Not explicitly dropped |
| `minimum_nights` outliers | Not clipped at ingestion | Capped | **Clipped at 99th percentile** |
| Written justification per column | ✗ | Partial | **✓ Full CSV with justification column** |

**Codex produced the most rigorous ingestion artefact.** Dropping `host_id` is the correct DS decision (it is an identifier, not a feature) and documenting every decision in a structured CSV with a justification column is a level of rigour neither Claude nor Antigravity matched.

### Task 01 — Agreements and disagreements

**Agreed**
- All three correctly identified and reported missingness: `last_review` and `reviews_per_month` at 20.56%; `name` and `host_name` negligible.
- All treated `reviews_per_month` NaN as semantically zero (fill with 0).
- No target leakage: no agent used target variable to decide missingness handling.

**Disagreed**
- **Schema log format:** Claude produced `.txt` (rubric expected `.md`) → automated check failed.
- **Column drops:** Only Codex dropped `host_id` (identifier) and `last_review` (high missingness, date-type).
- **Outliers at ingestion:** Codex clipped `minimum_nights` at 99th percentile; Antigravity capped price at $1,000; Claude only flagged, did not remove.

### Task 01 — Takeaway

Ingestion quality directly affects downstream tasks. The most robust approach: (1) per-column missingness justification (like Codex), (2) drop non-features (`host_id`) and document it, (3) use path checks so that 0-row loads fail fast instead of propagating silently.

---

## Task 02 — Exploratory Data Analysis

### What each agent was asked to do
Explore `price` distribution, feature-target relationships, and geographic patterns. Produce ≥3 plots with markdown interpretation, `eda_cleaned.csv`, and `eda_summary.md`.

### Task 02 — At a glance

| Agent | Plots | `eda_cleaned.csv` | Price cleaning | `minimum_nights` | EDA → Task 04 link |
|-------|-------|--------------------|----------------|------------------|--------------------|
| **Claude** | 9 (incl. geo, pairplot, top neighbourhoods) | Yes; price > 99th removed | 99th percentile | Clip at 30 | Explicit FE list: geo-cluster, target enc, interactions |
| **Antigravity** | 3 (distribution, correlation, feature vs target) | Yes; price=0 dropped, cap $1000 | Hard $1,000 cap | Cap 365 | TargetEncoding + spatial clustering suggested |
| **Codex** | 8 (incl. geo, borough×room heatmap, boxplot) | Yes; price > 99.5th removed | 99.5th percentile (~$1000) | Clip at 365 | Borough×room_type, spatial features, non-linear transforms |

### Plot comparison

| Plot type | Claude | Antigravity | Codex |
|---|---|---|---|
| Price distribution (raw) | ✓ | ✓ | ✓ |
| Price distribution (log) | ✓ | ✓ | ✓ |
| Correlation heatmap | ✓ | ✓ | ✓ |
| Price by room type | ✓ | ✓ | ✓ |
| Price by borough | ✓ | ✓ | ✓ |
| Geographic scatter (lat/lon) | ✓ | — | ✓ |
| Borough × room type heatmap | ✓ | — | ✓ |
| Top neighbourhoods | ✓ | — | — |
| Pairplot | ✓ | — | — |
| **Total plots** | **9** | **3** | **8** |

---

### Price Distribution

**Claude**
![Price Distribution — Claude](../agents/claude/task_02/outputs/price_distribution.png)

**Codex**
![Price Distribution — Codex](../agents/codex/task_02_codex/output_02_codex/price_distribution_hist.png)

**Antigravity**
![Price Distribution — Antigravity](../agents/antigravity/task_02/outputs/plot_01_target_distribution.png)

All three agents correctly identified the right-skewed distribution and recommended `log1p(price)` as the regression target. Claude and Codex included a log-scale plot alongside the raw distribution; Antigravity produced a single histogram.

---

### Correlation Heatmap

**Claude**
![Correlation Heatmap — Claude](../agents/claude/task_02/outputs/correlation_with_log_price.png)

**Codex**
![Correlation Heatmap — Codex](../agents/codex/task_02_codex/output_02_codex/feature_correlation_heatmap.png)

**Antigravity**
![Correlation Heatmap — Antigravity](../agents/antigravity/task_02/outputs/plot_02_correlation_heatmap.png)

Key finding consistent across all agents: `longitude` has the strongest linear correlation with `price` (−0.26), followed by `calculated_host_listings_count`. Numeric features overall have weak linear correlations — flagging that a linear model will struggle without feature engineering.

---

### Geographic Price Pattern

**Claude**
![Geo Scatter — Claude](../agents/claude/task_02/outputs/geo_price_scatter.png)

**Codex**
![Geo Scatter — Codex](../agents/codex/task_02_codex/output_02_codex/geo_price_scatter.png)

Both Claude and Codex produced geographic scatter plots revealing the spatial price gradient (Manhattan centre = high price). Antigravity did not produce a geographic plot. This gap is significant — `latitude` and `longitude` are among the most predictive features after `room_type` and `neighbourhood_group`, and spatial visualisation of the gradient motivates the geo-clustering feature engineered in Task 04.

---

### Price by Borough and Room Type

**Claude — Price Heatmap (Borough × Room Type)**
![Borough Room Type Heatmap — Claude](../agents/claude/task_02/outputs/price_heatmap_borough_roomtype.png)

**Codex — Borough × Room Type**
![Borough Room Type — Codex](../agents/codex/task_02_codex/output_02_codex/borough_roomtype_median_price_heatmap.png)

**Antigravity — Feature vs Target**
![Feature vs Target — Antigravity](../agents/antigravity/task_02/outputs/plot_03_feature_vs_target.png)

The Borough × Room Type interaction (Manhattan + Entire home/apt = highest prices) is the single most important structural insight from EDA. Claude and Codex both produced explicit interaction heatmaps. Antigravity's plot_03 shows a feature-vs-target relationship but does not decompose the interaction.

---

### Price by Room Type

**Claude**
![Price by Room Type — Claude](../agents/claude/task_02/outputs/price_by_room_type.png)

**Codex**
![Price by Room Type — Codex](../agents/codex/task_02_codex/output_02_codex/price_by_room_type.png)

Entire home/apt listings are consistently the highest-priced room type across all boroughs. Shared rooms cluster at the lower end. This categorical split is the single strongest predictor in the dataset and motivates including `room_type` as a primary feature in every model.

---

### Price by Borough

**Claude**
![Median Price by Borough — Claude](../agents/claude/task_02/outputs/median_price_by_borough.png)

**Codex**
![Price by Borough — Codex](../agents/codex/task_02_codex/output_02_codex/price_by_borough.png)

Manhattan dominates. Brooklyn is a distant second. Bronx and Staten Island are at the lower end. This ordering is consistent across Claude and Codex and explains why `neighbourhood_group` is a core feature in both baselines.

---

### Price Distribution — Log Scale

**Codex — Log-transformed price**
![Log Price Distribution — Codex](../agents/codex/task_02_codex/output_02_codex/price_distribution_log_hist.png)

**Codex — Price boxplot**
![Price Boxplot — Codex](../agents/codex/task_02_codex/output_02_codex/price_boxplot.png)

The log-transformed distribution is approximately normal — confirming why `log1p(price)` is the correct regression target. The boxplot clearly shows the extreme upper tail that distorts any model trained on raw price.

---

### Numeric Feature Distributions (Claude)
![Numeric Distributions — Claude](../agents/claude/task_02/outputs/numeric_distributions.png)

`minimum_nights`, `number_of_reviews`, and `calculated_host_listings_count` are all right-skewed — the same pattern as `price`. This motivates the log1p transforms applied to these features in Claude's Task 04 feature engineering.

---

### Top Neighbourhoods by Price (Claude)
![Top Neighbourhoods — Claude](../agents/claude/task_02/outputs/top_neighbourhoods_price.png)

Fort Wadsworth, Tribeca, and Sea Gate are the highest-median-price neighbourhoods. This plot is why `neighbourhood` (221 levels, excluded from the baseline) is worth reintroducing via target encoding in Task 04 — within-borough neighbourhood variation is large and predictively valuable.

---

### EDA Summary — Key findings compared

| Finding | Claude | Antigravity | Codex |
|---|---|---|---|
| `price` needs log1p transform | ✓ | ✓ | ✓ |
| `room_type` = top predictor | ✓ | ✓ | ✓ |
| Borough = major structural driver | ✓ | ✓ | ✓ |
| `neighbourhood` needs target encoding | ✓ | ✓ | — |
| Geo-clustering from lat/lon | ✓ | Suggested | ✓ |
| `reviews_per_month` and `number_of_reviews` collinear | ✓ | ✓ | Partial |
| Outlier cap applied | 99th percentile | **$1,000 flat** | 99.5th percentile |

**The outlier cap difference matters downstream.** Antigravity's hard $1,000 cap removed a larger portion of the upper tail than the percentile-based approaches. This reduced training signal for high-price listings and inflated RMSE in Tasks 03 and 04 by an estimated ~$31.

### Task 02 — Agreements and disagreements

**Agreed**
- `price` is strongly right-skewed; all recommend `log1p(price)` as regression target.
- `room_type` and `neighbourhood_group` (borough) are the dominant structural drivers; Manhattan + entire home/apt = highest subgroup.
- Geographic coordinates (`latitude`, `longitude`) carry spatial price signal; numeric review/availability features have weak linear correlation.

**Disagreed**
- **Outlier cap:** Claude 99th percentile; Codex 99.5th; Antigravity flat $1,000 → Antigravity’s cap is most aggressive and correlates with weakest Task 03/04 RMSE.
- **Breadth of EDA:** Claude 9 plots (geo, pairplot, top neighbourhoods); Codex 8; Antigravity 3 — geographic and interaction heatmaps only from Claude and Codex.
- **`neighbourhood`:** Claude and Antigravity explicitly recommend target encoding for Task 04; Codex mentions spatial/borough×room_type but not target encoding.

### Task 02 — Takeaway

EDA drives modelling: the log-target recommendation was followed by Claude and Antigravity in Task 03 but missed by Codex, with large impact. Conservative outlier trimming (e.g. 99th percentile) preserves signal; a flat $1,000 cap can over-trim and hurt final RMSE. Geographic and interaction plots (borough×room_type) directly motivate the best Task 04 feature engineering.

---

## Task 03 — Baseline Model

### What each agent was asked to do
80/20 train/test split with SEED=42. Preprocessing fitted on train only. Report RMSE, MAE, R². Save model + results CSV.

### Task 03 — At a glance

| Agent | Model | Target | Features (categorical) | Test RMSE | Test R² | Overfit? |
|-------|-------|--------|------------------------|-----------|--------|----------|
| **Claude** | Ridge | log1p(price) | room_type, neighbourhood_group (one-hot); neighbourhood excluded | **83.32** | **0.549** | No (train≈test) |
| **Antigravity** | Ridge (TransformedTargetRegressor) | log1p(price) | room_type, neighbourhood_group (one-hot) | 115.18 | 0.236 | — |
| **Codex** | LinearRegression | **raw price** | room_type, neighbourhood_group + imputation | 150.58 | **−0.625** | N/A (no fit) |

### Results

| Agent | Model | RMSE (USD) | MAE (USD) | R² | Log transform? |
|---|---|---|---|---|---|
| **Claude** | Ridge Regression | **83.32** | **47.95** | **0.549** | ✓ log1p |
| **Antigravity** | Ridge Regression | 115.18 | 56.34 | 0.236 | ✓ TransformedTargetRegressor |
| **Codex** | Linear Regression | 150.58 | 106.23 | **−0.625** | ✗ raw price |

R² = −0.625 means Codex's model is **worse than predicting the mean price for every listing**. This is a critical failure — the pipeline ran with no errors, produced a valid-looking CSV, and would have been submitted as a baseline without cross-agent comparison to flag it.

### Predicted vs Actual

**Claude**
![Predicted vs Actual — Claude](../agents/claude/task_03/outputs/predicted_vs_actual.png)

**Antigravity**
![Predicted vs Actual — Antigravity](../agents/antigravity/task_03/outputs/plot_actual_vs_predicted.png)

**Codex**
![Predicted vs Actual — Codex](../agents/codex/task_03_codex/output_03_codex/predicted_vs_actual.png)

Claude and Antigravity show the characteristic funnel shape of a model that fits mid-range prices but underpredicts the upper tail — acceptable for a linear baseline. Codex's plot shows near-random scatter around the diagonal, consistent with R² ≈ 0 (or worse).

### Residual Plots

**Claude**
![Residuals — Claude](../agents/claude/task_03/outputs/residual_plots.png)

**Antigravity**
![Residuals — Antigravity](../agents/antigravity/task_03/outputs/plot_residuals.png)

**Codex**
![Residuals — Codex](../agents/codex/task_03_codex/output_03_codex/residuals_plot.png)

Claude's residuals show heteroscedasticity (increasing variance at high predicted prices) — correctly diagnosed in the Task 04 improvement plan. Antigravity shows a similar pattern. Codex's residuals have no systematic structure because the model failed to learn any meaningful signal.

### Model Coefficients (Claude — Ridge)
![Model Coefficients — Claude](../agents/claude/task_03/outputs/model_coefficients.png)

The coefficient plot confirms the EDA findings: `room_type_Entire home/apt` and `neighbourhood_group_Manhattan` carry the largest positive weights. Geographic coordinates (`latitude`, `longitude`) contribute meaningful signal even in the linear model.

---

### Code comparison — what each agent built

**Claude** — Chose Ridge Regression explicitly because OLS has instability after one-hot encoding. Excluded `neighbourhood` (200+ levels) with written justification. Saved both train and test metrics to check for overfitting (Train RMSE = 83.65, Test = 83.32 — no overfitting).

```python
# Claude Task 03 — pipeline structure
pipeline = Pipeline([
    ('preprocessor', ColumnTransformer([
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])),
    ('model', Ridge(alpha=1.0))
])
# target: log1p(y_train), predictions back-transformed with expm1()
```

**Antigravity** — Used `TransformedTargetRegressor` to wrap the log transform cleanly inside the pipeline rather than transforming `y` manually.

```python
# Antigravity Task 03 — TransformedTargetRegressor pattern
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('model', TransformedTargetRegressor(
        regressor=Ridge(), func=np.log1p, inverse_func=np.expm1
    ))
])
```

**Codex** — Plain `LinearRegression` on raw `price`. Preprocessing inside a Pipeline (correct), but no target transform.

```python
# Codex Task 03 — missing log transform
pipeline = Pipeline([
    ('preprocessor', ColumnTransformer([
        ('num', Pipeline([('imputer', SimpleImputer(strategy='median')),
                          ('scaler', StandardScaler())]), numeric_features),
        ('cat', Pipeline([('imputer', SimpleImputer(strategy='most_frequent')),
                          ('ohe', OneHotEncoder(handle_unknown='ignore'))]), categorical_features)
    ])),
    ('model', LinearRegression())
])
# No log1p on y — this is the root cause of R² = −0.625
```

### Task 03 — Why results differ

- **Claude vs Antigravity (83 vs 115 RMSE):** Both use Ridge + log target. The gap comes from (1) Task 02 cleaning — Claude keeps more of the upper tail; (2) feature set and scaling choices; (3) possible differences in `eda_cleaned` row counts and preprocessing.
- **Codex (150.58, R² −0.625):** Raw `price` makes squared-error loss dominated by extreme listings; the model fails to learn a useful mapping. No code bug — a modelling assumption (no transform) that violates EDA recommendations.

### Task 03 — Agreements and disagreements

**Agreed**
- All used an 80/20 split with a fixed seed (42); preprocessing inside a Pipeline fitted on train only.
- All reported RMSE, MAE, and R² in USD (or equivalent).
- Categoricals: at least `room_type` and `neighbourhood_group`; numeric features scaled or imputed.

**Disagreed**
- **Target:** Claude and Antigravity used log1p(price); Codex used raw price → Codex baseline is invalid (worse than mean).
- **Regularisation:** Claude and Antigravity used Ridge; Codex used plain OLS → instability with one-hot and skewed target.
- **`neighbourhood`:** Claude explicitly excluded (high cardinality) with written justification; others did not exclude or used different handling.

### Task 03 — Takeaway

A “minimal” baseline must still be *statistically valid*: R² &gt; 0 and preferably comparable to a naive predictor. Applying the EDA recommendation (log1p(price)) in the baseline avoids silent failure and makes Task 04 improvements interpretable. Ridge (or similar) is safer than plain OLS after one-hot encoding.

---

## Task 04 — Improving Performance

### What each agent was asked to do
Diagnose the baseline weaknesses, implement ≥2 improvement strategies, compare honestly against baseline, save improved model + results.

### Task 04 — At a glance

| Agent | Strategies compared | Best model | Best RMSE | vs own baseline | Neighbourhood handling |
|-------|---------------------|------------|-----------|----------------|------------------------|
| **Claude** | Ridge (no FE) · Ridge+FE · RF+FE | Random Forest + FE | **74.87** | −10.1% | Target encoding + geo-cluster (k=20) |
| **Antigravity** | HistGradientBoosting + TargetEncoder | HistGradientBoostingRegressor | 106.07 | −7.9% | TargetEncoder in Pipeline |
| **Codex** | Linear baseline · RF · Gradient Boosting | Random Forest + FE | 86.53 | −42.5%* | One-hot (no target encoding) |

*\*Codex’s large % improvement is recovery from a broken baseline.*

### Results

| Agent | Best Model | RMSE (USD) | MAE (USD) | R² | vs own baseline |
|---|---|---|---|---|---|
| **Claude** | Random Forest + Feature Engineering | **74.87** | **42.59** | **0.485** | −10.1% |
| **Antigravity** | HistGradientBoosting + TargetEncoder | 106.07 | 50.59 | 0.352 | −7.9% |
| **Codex** | Random Forest + Feature Engineering | 86.53 | 48.47 | 0.463 | −42.5%* |

*\*Codex's 42.5% improvement is recovery from a broken baseline, not genuine advancement. Starting from a comparable baseline (83.32), Codex's final 86.53 is still worse than Claude's baseline.*

### Baseline Diagnosis (Claude — before improvement)
![Baseline Diagnosis — Claude](../agents/claude/task_04/outputs/baseline_diagnosis.png)

![Baseline Residuals by Borough — Claude](../agents/claude/task_04/outputs/baseline_residuals_by_borough.png)

The per-borough residual breakdown shows Manhattan listings are most under-predicted — the baseline model's borough-level one-hot encoding misses the within-borough price variation driven by specific neighbourhoods and lat/lon clusters. This directly motivates the neighbourhood target encoding and geo-clustering added in Task 04.

---

### Model comparison charts

**Claude — Strategy comparison**
![Model Comparison — Claude](../agents/claude/task_04/outputs/model_comparison.png)

**Codex — Baseline vs Improved**
![Baseline vs Improved — Codex](../agents/codex/task_04_codex/output_04_codex/baseline_vs_improved_metrics.png)

### Predicted vs Actual — Improved models

**Claude**
![Improved Predicted vs Actual — Claude](../agents/claude/task_04/outputs/predicted_vs_actual_comparison.png)

**Antigravity**
![Improved Predicted vs Actual — Antigravity](../agents/antigravity/task_04/outputs/plot_improved_actual_vs_predicted.png)

**Codex**
![Improved Predicted vs Actual — Codex](../agents/codex/task_04_codex/output_04_codex/improved_predicted_vs_actual.png)

### Feature Importances (Claude — Random Forest)
![RF Feature Importances — Claude](../agents/claude/task_04/outputs/rf_feature_importances.png)

Top features: `neighbourhood_target_enc`, `room_type`, `geo_cluster`, `longitude`. The neighbourhood target encoding and geo-clustering (both new in Task 04) are the two most important features — confirming the EDA insight that spatial and location features dominate price prediction.

### Improved Residuals (Codex)
![Improved Residuals — Codex](../agents/codex/task_04_codex/output_04_codex/improved_residuals_plot.png)

Codex's Task 04 residuals show a much tighter spread than its Task 03 residuals (which were near-random scatter due to R²=−0.625). The residual pattern now resembles Claude and Antigravity's Task 03 baselines — confirming that the model switch fixed the fundamental issue.

---

### Improvement strategies compared

**Claude** implemented two explicit strategies side-by-side:

| Strategy | RMSE | R² |
|---|---|---|
| Baseline (Ridge, no FE) | 83.32 | 0.362 |
| Strategy A: Ridge + Feature Engineering | 80.09 | 0.410 |
| Strategy B: Random Forest + Feature Engineering | **74.87** | **0.485** |

Feature engineering applied (all fitted on train only):
- `neighbourhood_target_enc` — mean log1p(price) per neighbourhood, out-of-fold to prevent leakage
- `geo_cluster` — k-means (k=20) on lat/lon, fitted on train only
- `room_type × neighbourhood_group` interaction
- log1p transforms on `minimum_nights`, `number_of_reviews`, `calculated_host_listings_count`
- Binary flags: `has_reviews`, `is_professional_host`

**Antigravity** switched to `HistGradientBoostingRegressor` + `TargetEncoder` for `neighbourhood`. Critically, the TargetEncoder was placed **inside the Pipeline** — the correct implementation that prevents target leakage.

```python
# Antigravity Task 04 — TargetEncoder correctly inside Pipeline
preprocessor = ColumnTransformer([
    ('target_enc', TargetEncoder(), ['neighbourhood']),
    ('ohe', OneHotEncoder(handle_unknown='ignore'), ['room_type', 'neighbourhood_group']),
    ('num', StandardScaler(), numeric_features)
])
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('model', TransformedTargetRegressor(
        regressor=HistGradientBoostingRegressor(random_state=42),
        func=np.log1p, inverse_func=np.expm1
    ))
])
```

**Codex** compared Random Forest vs Gradient Boosting and selected Random Forest:

| Strategy | RMSE | R² |
|---|---|---|
| Baseline (Linear, no log) | 150.58 | −0.625 |
| Gradient Boosting + FE | 89.07 | 0.431 |
| **Random Forest + FE** | **86.53** | **0.463** |

### Failures caught in Task 04

**Claude — LightGBM validation contamination** (caught, fixed in Iteration 2)

```python
# WRONG — leaks validation labels into training
lgbm.fit(X_train, y_train, eval_set=[(X_val, y_val)])

# CORRECT — internal split for early stopping only
X_tr, X_inner_val, y_tr, y_inner_val = train_test_split(
    X_train, y_train, test_size=0.1, random_state=42)
lgbm.fit(X_tr, y_tr, eval_set=[(X_inner_val, y_inner_val)])
```

This failure would not raise an error and would not be detected by any automated test. It gives LightGBM an information advantage in model comparison, potentially selecting an inferior model. Caught by manually reading the training code.

**Claude — Feature importance hardcoded** (caught, fixed in Iteration 3)

```python
# WRONG — always shows LightGBM importances regardless of best model
model_for_importance = 'LightGBM-Tuned' if 'LightGBM-Tuned' in models else 'LightGBM'

# CORRECT — derives from actual best model
best_model_name = results_df.loc[results_df['RMSE_USD'].idxmin(), 'model']
model_for_importance = best_model_name
```

**Codex** — Diagnosed that baseline failure was the missing log transform and corrected it in Task 04 by switching to Random Forest (more robust to skewed targets without explicit transform).

### Task 04 — Agreements and disagreements

**Agreed**
- All moved from a linear baseline to a tree-based (or ensemble) model for Task 04; all reported improvement in RMSE/MAE/R² over their own baseline.
- Preprocessing and encoders fitted on train only (Pipeline or equivalent); no test set used for feature or model decisions.
- Multiple strategies were attempted (Claude: Ridge+FE vs RF+FE; Codex: RF vs GB; Antigravity: HistGradientBoosting + TargetEncoder).

**Disagreed**
- **Best model choice:** Claude and Codex chose Random Forest; Antigravity chose HistGradientBoostingRegressor. In this benchmark, RF (Claude 74.87, Codex 86.53) outperformed HGBR (Antigravity 106.07).
- **Feature engineering:** Claude added explicit FE (target encoding, geo-cluster, interactions, log1p on numerics); Codex added FE with RF/GB; Antigravity relied on TargetEncoder + tree model without the same breadth of FE.
- **Validation discipline:** Claude initially used validation set for LightGBM early stopping (caught and fixed); others did not use early stopping on the comparison set.

### Task 04 — Takeaway

Improvement is interpretable only when the baseline is valid: Codex’s “42.5% improvement” is mostly fixing the baseline. Random Forest plus rich feature engineering (target encoding, geo-clusters, interactions) gave the best RMSE here. When using early stopping or target-derived features, keep comparison validation strictly separate from any fitting or tuning.

---

## Models Built and Leakage Prevention

### What each agent built across Tasks 03 and 04

#### Claude

**Task 03 — Ridge Regression on log1p(price)**

Ridge was chosen as the baseline because one-hot encoding `room_type` and `neighbourhood_group` produces mild multicollinearity; Ridge's L2 regularisation stabilises coefficients without discarding features. Plain OLS was rejected explicitly. `neighbourhood` (221 levels) was excluded at baseline and reintroduced in Task 04 via target encoding.

```
Input features (Task 03):
  Categorical (one-hot): room_type, neighbourhood_group
  Numeric (StandardScaler): latitude, longitude, minimum_nights,
    number_of_reviews, reviews_per_month,
    calculated_host_listings_count, availability_365
Target: log1p(price) → predictions back-transformed with expm1()
```

**Task 04 — Two strategies compared:**

*Strategy A — Ridge + Feature Engineering* (isolates feature impact from model impact)
*Strategy B — Random Forest + Feature Engineering* (combined improvement)

New features added (all fitted on X_train only):

| Feature | How built | Leakage risk | How we prevented it |
|---|---|---|---|
| `neighbourhood_target_enc` | Mean log1p(price) per neighbourhood | Target encoded on train → applied to test | Computed on X_train only, never using any test rows |
| `geo_cluster` | k-means (k=20) on lat/lon | Cluster centres could be fit on all data | `KMeans.fit()` called on X_train only; test rows assigned via `predict()` |
| `log1p(minimum_nights)` | log transform | None | Stateless transform |
| `log1p(number_of_reviews)` | log transform | None | Stateless transform |
| `room_type × neighbourhood_group` | String concatenation | None | Stateless transform |
| `has_reviews` | `number_of_reviews > 0` | None | Stateless transform |
| `is_professional_host` | `calculated_host_listings_count > 1` | None | Stateless transform |

---

#### Antigravity

**Task 03 — Ridge via TransformedTargetRegressor**

Wrapping the log transform in `TransformedTargetRegressor(func=np.log1p, inverse_func=np.expm1)` is a clean pattern: the pipeline handles the inverse transform automatically when calling `.predict()`, removing the risk of forgetting to call `expm1()` on predictions.

**Task 04 — HistGradientBoostingRegressor + TargetEncoder**

`HistGradientBoostingRegressor` was chosen because it handles high-cardinality categoricals and non-linear spatial interactions natively without explicit feature engineering. The key methodological decision was using scikit-learn's `TargetEncoder` for `neighbourhood`.

**Why TargetEncoder is a leakage risk if used naively:**
A naive target encoding computes the mean price per neighbourhood on the full training set. Each training row's own price then contributes to the encoding of its own neighbourhood — this is a form of target leakage that inflates in-sample performance.

**How Antigravity prevented it:**
Sklearn's `TargetEncoder` uses cross-validation smoothing internally: when fitting, each fold's neighbourhood encoding is computed from out-of-fold rows only. By placing `TargetEncoder` inside the Pipeline, this happens correctly on every train fold.

```python
# Correct — TargetEncoder inside Pipeline.fit() uses CV smoothing automatically
preprocessor = ColumnTransformer([
    ('target_enc', TargetEncoder(), ['neighbourhood']),
    ('ohe', OneHotEncoder(handle_unknown='ignore'),
           ['room_type', 'neighbourhood_group']),
    ('num', StandardScaler(), numeric_features)
])
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('model', TransformedTargetRegressor(
        regressor=HistGradientBoostingRegressor(random_state=42),
        func=np.log1p, inverse_func=np.expm1
    ))
])
pipeline.fit(X_train, y_train)  # TargetEncoder CV smoothing happens here
```

---

#### Codex

**Task 03 — LinearRegression (no log transform)**

`price` was used as the raw target. This caused the squared-error loss to be dominated by extreme-price listings (some above $500), preventing the model from learning to predict typical listings. Result: R² = −0.625.

**Task 04 — Random Forest and GradientBoostingRegressor (two compared)**

Switching to Random Forest bypassed the log-transform requirement because tree-based models split on rank order, not magnitude — extreme values influence splits but do not dominate the loss function the same way. Both strategies used feature engineering and a scikit-learn Pipeline.

| Strategy | RMSE | R² |
|---|---|---|
| Gradient Boosting + FE | 89.07 | 0.431 |
| Random Forest + FE | **86.53** | **0.463** |

Random Forest was selected. The improvement over Task 03 (RMSE 150.58 → 86.53) is large but partly reflects recovery from the broken baseline rather than a genuine advancement.

---

### Train / Test Split — all agents

All three agents used an 80/20 stratified split with `SEED = 42`. This was enforced in the task prompt and verified in each agent's report file.

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

The test set was used only once — for final metric reporting. No agent used test-set information for feature selection, hyperparameter tuning, or preprocessing decisions (verified by reading each notebook's cell order).

---

### How we checked for data leakage

Leakage can enter a DS pipeline at three points. We checked each one.

**1. Preprocessing leakage (scaler / encoder fitted before split)**

All three agents used scikit-learn Pipelines, which guarantee that `.fit()` is called only on training data when used correctly. We verified this by checking that `pipeline.fit(X_train, y_train)` was the first fit call in each notebook — there was no call to `scaler.fit(X)` on the full dataset before the split.

| Check | Claude | Antigravity | Codex |
|---|---|---|---|
| Scaler fitted on X_train only | ✓ | ✓ | ✓ (Task 04 only — Task 03 had no scaler leakage but also no log transform) |
| Encoder fitted on X_train only | ✓ | ✓ | ✓ |
| No `.fit()` before `train_test_split` | ✓ | ✓ | ✓ |

**2. Target encoding leakage**

Target encoding (encoding a categorical by the mean of the target) leaks target information if computed on the full dataset before splitting, or if a row's own target value contributes to its own encoding.

- **Claude** computed neighbourhood mean prices on `X_train` only, then applied `.transform()` to `X_test` using those train-derived means. Verified by reading the `FunctionTransformer` in the pipeline.
- **Antigravity** used sklearn's `TargetEncoder` inside the Pipeline — CV smoothing prevents each row contributing to its own encoding. Verified by checking that `TargetEncoder` appeared inside `ColumnTransformer` inside `Pipeline.fit()`.
- **Codex** did not use target encoding in Task 04 — no leakage risk from this source.

**3. Validation contamination (early stopping)**

This is the hardest leakage to detect because it does not raise an error and produces plausible results.

Claude's first draft of Task 04 included LightGBM with:
```python
# WRONG — X_val/y_val are the comparison validation set
lgbm.fit(X_train, y_train, eval_set=[(X_val, y_val)])
```

LightGBM uses the `eval_set` to decide when to stop adding trees. If `X_val` is the same set used for final metric comparison, LightGBM has seen validation labels during training while Ridge and RF have not — an unfair advantage that inflates LightGBM's apparent performance.

**Fix applied (Iteration 2):**
```python
# CORRECT — separate internal split from X_train for early stopping
X_tr, X_inner_val, y_tr, y_inner_val = train_test_split(
    X_train, y_train, test_size=0.1, random_state=42
)
lgbm.fit(X_tr, y_tr, eval_set=[(X_inner_val, y_inner_val)])
# X_val remains completely untouched until final comparison
```

After the fix, Random Forest still outperformed LightGBM (RMSE 74.87 vs ~77), confirming the original ranking was correct despite the contamination being removed.

---

### Summary — leakage prevention measures

| Leakage type | Claude | Antigravity | Codex | Verified how |
|---|---|---|---|---|
| Preprocessing before split | ✓ None | ✓ None | ✓ None | Cell order in each notebook |
| Target encoding on full dataset | ✓ Train-only | ✓ Pipeline CV smoothing | N/A | Code review of fit calls |
| Early stopping on comparison val set | ✓ Fixed (Iter 2) | N/A | N/A | Manual code review |
| Test set used for feature decisions | ✓ None | ✓ None | ✓ None | Cell order in each notebook |
| EDA on test data | ✓ None | ✓ None | ✓ None | No train/test split in Task 02 |

### Leakage as a scored benchmark dimension

Most group benchmarks compare only RMSE. We went further: leakage prevention was turned into a **formal, programmatic metric** scored alongside task performance.

**Script:** [`group-coursework/tasks/leakage_check.py`](../tasks/leakage_check.py)

The script parses each agent's Task 03 and Task 04 notebooks as JSON and applies five binary checks — each worth 1 point:

| Criterion | What is checked |
|---|---|
| **L1** — split present | `train_test_split`, saved index arrays, or `split_meta.pkl` found in notebook |
| **L2** — split before fit | First `.fit()` call appears in a later cell (or lower line) than the split |
| **L3** — Pipeline used | `sklearn.Pipeline` / `ColumnTransformer` wraps all preprocessing steps |
| **L4** — no fit on full X | No `.fit(X` or `.fit_transform(X` on the un-split dataset detected |
| **L5** — target encoding safe | Either sklearn `TargetEncoder` (cross-validated by design) or train-only `groupby` |

**Results — all six notebooks scored 5/5:**

| Agent | Tool | Task | L1 | L2 | L3 | L4 | L5 | Score |
|---|---|---|---|---|---|---|---|---|
| dilara | Claude | Task 03 | ✓ | ✓ | ✓ | ✓ | N/A ✓ | **5/5** |
| dilara | Claude | Task 04 | ✓ | ✓ | ✓ | ✓ | ✓ train-only groupby | **5/5** |
| caroline | Antigravity | Task 03 | ✓ | ✓ | ✓ | ✓ | N/A ✓ | **5/5** |
| caroline | Antigravity | Task 04 | ✓ | ✓ | ✓ | ✓ | ✓ sklearn TargetEncoder | **5/5** |
| moham | Codex | Task 03 | ✓ | ✓ | ✓ | ✓ | N/A ✓ | **5/5** |
| moham | Codex | Task 04 | ✓ | ✓ | ✓ | ✓ | N/A ✓ | **5/5** |

**Mean leakage score: 5.00 / 5. All agents passed all criteria.**

The 5/5 result is itself a finding: all three LLM tools have internalised scikit-learn best practices around Pipelines and train-only fitting. The nuanced difference lies in *how* target encoding leakage is handled:

- **Antigravity** used sklearn's `TargetEncoder` — the most robust approach, because cross-validation smoothing is built into the transformer itself, making it impossible to accidentally leak even within a single training fold.
- **Claude** used a manual `df_train.groupby('neighbourhood')['log_price'].mean()` — correct, but requires the developer to be disciplined about variable scope. One mistyped `df` instead of `df_train` would cause silent leakage.
- **Codex** avoided neighbourhood encoding entirely at Task 04 — no leakage risk, but also forfeited the signal.

The one real leakage event in the project — Claude's LightGBM `eval_set` contamination — was caught by human review and fixed in Iteration 2, not by any automated check. This confirms that programmatic checks are necessary but not sufficient: subtle validation-set contamination requires reading the training loop, not just checking cell order.

---

## Performance Summary

### RMSE across all tasks

| Agent | Task 03 RMSE | Task 04 RMSE | Improvement |
|---|---|---|---|
| Claude | 83.32 | **74.87** | −8.45 USD |
| Antigravity | 115.18 | 106.07 | −9.11 USD |
| Codex | 150.58 | 86.53 | −64.05 USD* |

*Codex's large drop is recovery from a broken baseline.

### The compounding effect of Task 02 cleaning decisions

Antigravity's hard $1,000 price cap (vs Claude's 99th-percentile cut) removed more of the upper tail from training data. This gap persisted through both modelling tasks and cannot be recovered by model improvement alone:

- Antigravity Task 03: +31.86 RMSE vs Claude
- Antigravity Task 04: +31.20 RMSE vs Claude

The gap is almost constant — confirming it originates in Task 02, not model choice.

---

## Verdict

### By task

| Task | Winner | Why |
|---|---|---|
| Task 01 | **Codex** | Most rigorous missingness report with per-column justification; dropped `host_id` correctly |
| Task 02 | **Claude** | 9 plots vs 3, geographic and interaction analysis, FE plan for Task 04 |
| Task 03 | **Claude** | Only coherent baseline (R²=0.549); Codex R²=−0.625 is a modelling failure |
| Task 04 | **Claude** | Best absolute RMSE (74.87), two strategies compared, all failures caught and documented |

### Overall

| Priority | Best agent |
|---|---|
| Best predictive model | **Claude** — RMSE 74.87, R² 0.485 |
| Most reliable / fewest silent failures | **Antigravity** — all failures raised visible errors |
| Fastest to acceptable output | **Antigravity** — 100 mins, ~1.5 iterations/task |
| Best documentation / output structure | **Codex** — highest rubric score (19/20) |
| Worst statistical validity | **Codex** — R²=−0.625 baseline |

**The central finding:** Rubric score (Codex 19/20) and predictive quality (Claude RMSE 74.87) point in opposite directions. A pipeline that produces well-named, correctly formatted files can still be statistically broken. **The rubric catches what is present; human review catches whether it is correct.**

---

## Failure Mode Catalogue

| Failure | Agent | Task | Danger | How caught |
|---|---|---|---|---|
| 0-row silent load | Claude | 01 | ⚠️ High — propagates undetected | Manual file size check |
| Missing output files | Claude | 01 | Medium — rubric penalty | evaluate.py |
| No log transform on target | Codex | 03 | ⚠️ High — R²=−0.625, no error | Cross-agent comparison |
| LightGBM validation contamination | Claude | 04 | ⚠️ High — biases model selection | Manual code review |
| Feature importance hardcoded | Claude | 04 | Medium — misleading report | Manual plot review |
| Notebook JSON corruption | Antigravity | Rename | ⚠️ High — unexecutable notebooks | nbformat crash |
| Absolute path (first run) | Antigravity | 01 | Low — immediate error | Runtime error |
| Environment/backend assumptions | Codex | 02–03 | Medium — blocked output | Runtime error |
| No rejected approaches documented | Antigravity | 04 | Low — documentation gap | Manual review |

---

## Verification Checklist

Run after every agent task before committing outputs:

- [ ] `assert len(df) > 0` immediately after loading any dataset
- [ ] Check file size of large outputs — ingested CSV should be >1MB
- [ ] Confirm R² > 0 for any regression model before using it as a baseline
- [ ] Verify preprocessing is inside a Pipeline or explicitly fitted on `X_train` only
- [ ] If early stopping: confirm `eval_set` does not use the comparison validation set
- [ ] Check feature importance plots reference the actual best model object
- [ ] Confirm EDA recommendations (e.g. log transform) are applied in the next task prompt
- [ ] Clear notebook output cells before committing

---

## Appendix A — Per-task comparison matrix (dense)

One-row-per-agent summary for quick cross-task comparison.

**Task 01 — Ingestion**

| Agent | Key artefact | Main strength | Main weakness |
|-------|--------------|---------------|---------------|
| Claude | schema_log.txt, missingness_report.csv, outlier_flags | Correct semantics (reviews_per_month=0) | .txt not .md; 0-row path bug |
| Antigravity | schema_log.md, missingness_report, outlier_flags | Clean outputs; price=0 dropped, cap $1000 | First run absolute path |
| Codex | schema_log.md, missingness CSV with justification column | Per-column handling + justification; dropped host_id | Path drift after rename |

**Task 02 — EDA**

| Agent | Plots | Cleaning | Main strength | Main weakness |
|-------|-------|----------|---------------|---------------|
| Claude | 9 | 99th % price; min_nights≤30 | Geo, pairplot, top neighbourhoods; FE plan for T04 | — |
| Antigravity | 3 | $1000 cap; min_nights cap | Log-target + TargetEncoding suggestion | Fewer plots; aggressive cap |
| Codex | 8 | 99.5th % price; min_nights≤365 | Borough×room heatmap, boxplot, quantiles | No explicit target-encoding recommendation |

**Task 03 — Baseline**

| Agent | Model | Target | RMSE | R² | Main strength | Main weakness |
|-------|-------|--------|------|-----|---------------|---------------|
| Claude | Ridge | log1p(price) | 83.32 | 0.549 | Only valid baseline; written justification for excluding neighbourhood | Output naming mismatch |
| Antigravity | Ridge (TransformedTargetRegressor) | log1p(price) | 115.18 | 0.236 | Clean pipeline pattern | Weaker than Claude (cleaning + FE differ) |
| Codex | LinearRegression | raw price | 150.58 | −0.625 | Pipeline structure correct | Baseline invalid; no log transform |

**Task 04 — Improvement**

| Agent | Best model | RMSE | vs baseline | Main strength | Main weakness |
|-------|------------|------|-------------|---------------|---------------|
| Claude | RF + FE | 74.87 | −10.1% | Two strategies (Ridge+FE, RF+FE); best RMSE; leakage caught | LightGBM val contamination; hardcoded importance plot |
| Antigravity | HistGradientBoosting + TargetEncoder | 106.07 | −7.9% | TargetEncoder in Pipeline (no leakage) | Single strategy; no failed approaches documented |
| Codex | RF + FE | 86.53 | −42.5%* | RF vs GB compared; clear recovery | *Improvement inflated by broken baseline |

---

## Appendix B — All Scores

| tool | task_id | score | time_mins | notes |
|---|---|---|---|---|
| Claude | task_01_data_ingestion | 2 | 20 | schema_log.md missing; no per-column justification |
| Antigravity | task_01_data_ingestion | 5 | 15 | clean output with outlier flags |
| Codex | task_01_data_ingestion | 5 | 25 | task_01_complete |
| Claude | task_02_eda | 5 | 30 | 9 plots, eda_summary with FE recommendations |
| Antigravity | task_02_eda | 4 | 20 | 3 plots, notebook outputs not cleared |
| Codex | task_02_eda | 4 | 25 | task_02_codex_eval |
| Claude | task_03_baseline_model | 4 | 35 | RMSE=83.32 R²=0.549; output naming mismatch |
| Antigravity | task_03_baseline_model | 5 | 30 | RMSE=115.18 |
| Codex | task_03_baseline_model | 5 | 30 | RMSE=150.58 R²=−0.625 |
| Claude | task_04_improving_performance | 5 | 45 | RF+FE RMSE=74.87 R²=0.485 |
| Antigravity | task_04_improving_performance | 4 | 35 | RMSE=106.07; no failed approaches documented |
| Codex | task_04_improving_performance | 5 | 40 | RF RMSE=86.53 R²=0.463 |
