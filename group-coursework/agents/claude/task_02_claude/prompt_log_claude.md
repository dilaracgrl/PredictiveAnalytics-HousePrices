# Prompt Log — Task 02: Exploratory Data Analysis

## Iteration 1
**Prompt:**
```
You are helping with a data science coursework project.
The dataset is the New York City Airbnb Open Data (2019).
Your input: ../task_01/outputs/ingested.csv
Project goal: predict Airbnb nightly listing price (regression on `price`).

Your job is Task 02: EDA and Insight Generation.
Work entirely inside this notebook. Save all outputs to outputs/.

SEED = 42

--- WHAT YOU NEED TO DELIVER ---

1. Understand the target variable
   Explore the distribution of `price` thoroughly.
   What does it look like? Is it well-behaved for modelling as-is?
   What does this tell you about how it should be treated in Task 03?
   Save your plots to outputs/ and write up your conclusions in markdown.

2. Explore the features
   Investigate the features available in the dataset.
   Which ones look most promising for predicting price?
   Are there patterns you would not have expected?
   Are there features that look redundant or problematic?
   This dataset has geographic coordinates, categorical location data,
   and review/availability metrics — explore all of them.

3. Understand relationships between features and price
   Go beyond correlation coefficients.
   What does the relationship between location and price actually look like?
   How does room type interact with neighbourhood?
   Are there subgroups in the data that behave very differently?

4. Make decisions about remaining data quality issues
   Your EDA may reveal further outliers or anomalies not caught in Task 01.
   Decide what to do with them and justify each decision in markdown.
   Save the final analysis-ready dataset to outputs/eda_cleaned.csv

5. Summarise your findings
   Write an EDA Summary section at the end of the notebook.
   This should answer: what are the most important features?
   What preprocessing does the target variable need?
   What feature engineering ideas does this data suggest for Task 04?
   Save this summary to outputs/eda_summary.md —
   it will be referenced in Tasks 03 and 04.

--- CONSTRAINTS (non-negotiable) ---

- Read from ingested.csv only — do not reload the raw file
- Do NOT create a train/test split in this notebook
- Do NOT use any held-out data
- Every plot must have a title, labelled axes, and a markdown interpretation cell
- Save all outputs to outputs/ using relative paths only
```
**What happened:**
The agent produced 9 plots: price distribution (raw and log1p), correlation heatmap, median price by borough, by room type, geographic scatter, neighbourhood price rankings, pairplot, and categorical counts. Each plot had an accompanying markdown interpretation cell. `eda_summary.md` was produced with key findings including the log1p transform recommendation, feature importance rankings, and a "Feature Engineering Recommendations for Task 04" section covering neighbourhood target encoding, geo-clustering, interaction terms, and log transforms on skewed numerics. `eda_cleaned.csv` was saved with price capped at the 99th percentile and `minimum_nights` clipped at 30. No test split was created. Scored 5/5.
