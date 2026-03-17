# Prompt Log: Task 02 - Exploratory Data Analysis (EDA)

> Paste each prompt you sent to the agent here, in order. Note what changed between iterations.

## Prompt Received
**Prompt:**
```
Prompt 2:
You are helping with a data science coursework project.
The dataset is the New York City Airbnb Open Data (2019).
Your input: ../task_01/outputs/ingested.csv
Project goal: predict Airbnb nightly listing price (regression on price).

Your job is Task 02: EDA and Insight Generation.
Work entirely inside this notebook. Save all outputs to outputs/.

SEED = 42

... (details omitted for brevity) ...

1. Understand the target variable
2. Explore the features
3. Understand relationships between features and price
4. Make decisions about remaining data quality issues (eda_cleaned.csv)
5. Summarise your findings (eda_summary.md)
```

## Decisions and Implementation Details
Task 02 demanded rigorous exploration of the dataset to dictate the architecture of the regression pipelines. The highest stricture was to analyze the raw data without imposing a train/test split.

1. **Target Variable Analysis (`price`)**:
   - Visualized the target via purely linear histograms. `price` demonstrated catastrophic right-skewness (ranging from $0 to $10,000 nightly) rendering mean-centric measurements unstable.
   - **Crucial Diagnostic Check:** Re-visualized with a log-scaled histogram (`np.log1p`). The `log_price` strongly emulated a normal distribution.
   - **Architectural Decision:** We definitively established that all downstream models must predict the log-transformed price (`log1p`), not raw absolute currency, to satisfy regression heteroscedasticity assumptions.

2. **Feature Explorations vs Target**:
   - **Mathematical Correlations**: Generated a seaborn correlation heatmap across numerical dimensions (`minimum_nights`, `reviews`, etc.). This proved that standard continuous variables share remarkably weak linear links to the target price.
   - **Categorical Power**: Built boxplots mapping `neighbourhood_group` and `room_type` against log `price`. The results definitively cemented structural categories (e.g. `Entire home/apt` located explicitly in `Manhattan`) as the overwhelming dictating baseline values of property price variance.
   
3. **Data Quality Execution (from Insights)**:
   - Armed with statistical EDA visibility, we formally dropped listings with `price <= 0` because free properties violate sensible valuation mechanics.
   - Filtered out `price > 1000` anomalies (clipping the >99th percentile) to protect Mean Squared Error scalars during model tuning.
   - Filtered listings with `minimum_nights > 365`. Long-term leases warp standard nightly BNB price dynamics.

**Output:** `eda_cleaned.csv` and `eda_summary.md` generated alongside `plot_01_target_distribution.png`, `plot_02_correlation_heatmap.png`, and `plot_03_feature_vs_target.png`.
