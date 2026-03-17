# Prompt Log: Task 01 - Data Ingestion

> Paste each prompt you sent to the agent here, in order. Note what changed between iterations.

## Prompt Received
**Prompt:**
```
Prompt 1:
You are helping with a data science coursework project.
The dataset is the New York City Airbnb Open Data (2019).
File location: ../../data/raw/AB_NYC_2019.csv
Project goal: predict Airbnb nightly listing price (regression on price).

Your job is Task 01: Data Ingestion, Schema Checks, and Missingness Handling.
Work entirely inside this notebook. Save all outputs to outputs/.

SEED = 42

... (details omitted for brevity) ...

1. Load and inspect the dataset (schema_log.txt)
2. Assess data quality (missingness_report.csv, outlier_flags.txt)
3. Make and justify cleaning decisions
4. Produce a clean dataset (ingested.csv)
```

## Decisions and Implementation Details
Task 01 involved foundational data ingestion, missingness imputation, and outlier flagging. This stage required strict adherence to data leakage boundaries. 

1. **Schema Check**:
   - The dataset structure (48,895 rows, 16 columns) was successfully read and validated into `schema_log.md`. Types were parsed cleanly, with spatial coordinates encoded as `float64` and generic strings as `object`.

2. **Missingness Identification & Handling Blueprint**:
   - We observed a 20.56% missingness rate specifically clustered in `last_review` and `reviews_per_month`. 
   - **Decision:** Rather than dropping 10,000+ rows (which would introduce severe response bias), we applied semantic sentinel filling. `last_review` nulls semantically imply the property has never been reviewed, thus imputed with `"No review"`. Consequently, `reviews_per_month` missingness logically infers a review frequency of `0.0`.
   - `name` and `host_name` exhibited negligible missingness (~0.04% combined). They were imputed with `"Unknown"`. This preserved index continuity while dropping zero records.

3. **Outlier Detection Strategy**:
   - Outliers were algorithmically flagged (`minimum_nights > 365`, `price <= 0`, `price > 5000`) and written to `outlier_flags.txt`.
   - **Crucial Decision:** No rows were removed at this phase. Standard practice strictly prohibits preemptively transforming or filtering based on the target variable (`price`) *before* Exploratory Data Analysis (EDA). By leaving the index intact, we guaranteed structural integrity and adhered to professional coursework constraints regarding premature bias.

**Output:** Un-leaked pipeline output saved to `agents/antigravity/task_01/outputs/ingested.csv`.
