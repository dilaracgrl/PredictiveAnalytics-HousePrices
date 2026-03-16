from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEED = 42
np.random.seed(SEED)

INPUT_PATH = Path("../task_01/outputs/ingested.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_PATH)

# Additional EDA-stage cleaning: remove the most extreme right tail in target to stabilize downstream modelling
price_cap = df["price"].quantile(0.995)
eda_df = df[df["price"] <= price_cap].copy()

# 1) Target distribution plots
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(df["price"], bins=80, color="#2a9d8f", edgecolor="white")
ax.set_title("Price Distribution (Original Scale)")
ax.set_xlabel("Price (USD/night)")
ax.set_ylabel("Listing Count")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "price_distribution_hist.png", dpi=160)
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(np.log1p(df["price"]), bins=80, color="#264653", edgecolor="white")
ax.set_title("Price Distribution (log1p for inspection only)")
ax.set_xlabel("log(1 + price)")
ax.set_ylabel("Listing Count")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "price_distribution_log_hist.png", dpi=160)
plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 5))
ax.boxplot(df["price"], vert=True, patch_artist=True, boxprops=dict(facecolor="#e9c46a"))
ax.set_title("Price Boxplot (Original Scale)")
ax.set_ylabel("Price (USD/night)")
ax.set_xticks([1])
ax.set_xticklabels(["price"])
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "price_boxplot.png", dpi=160)
plt.close(fig)

# 2) Feature exploration - correlation heatmap
num_cols = [
    "price", "minimum_nights", "number_of_reviews", "reviews_per_month",
    "calculated_host_listings_count", "availability_365", "latitude", "longitude"
]

corr = eda_df[num_cols].corr(numeric_only=True)
fig, ax = plt.subplots(figsize=(9, 7))
im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)
ax.set_xticks(range(len(num_cols)))
ax.set_xticklabels(num_cols, rotation=45, ha="right")
ax.set_yticks(range(len(num_cols)))
ax.set_yticklabels(num_cols)
ax.set_title("Numeric Feature Correlation Heatmap")
cbar = fig.colorbar(im, ax=ax)
cbar.set_label("Correlation")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "feature_correlation_heatmap.png", dpi=160)
plt.close(fig)

# 3) Price by room type (boxplot via matplotlib)
room_types = list(eda_df["room_type"].dropna().unique())
room_data = [eda_df.loc[eda_df["room_type"] == r, "price"].values for r in room_types]
fig, ax = plt.subplots(figsize=(8, 5))
ax.boxplot(room_data, patch_artist=True)
ax.set_xticks(range(1, len(room_types) + 1))
ax.set_xticklabels(room_types, rotation=20)
ax.set_title("Price by Room Type")
ax.set_xlabel("Room Type")
ax.set_ylabel("Price (USD/night)")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "price_by_room_type.png", dpi=160)
plt.close(fig)

# 4) Price by borough
boroughs = list(eda_df["neighbourhood_group"].dropna().unique())
borough_data = [eda_df.loc[eda_df["neighbourhood_group"] == b, "price"].values for b in boroughs]
fig, ax = plt.subplots(figsize=(8, 5))
ax.boxplot(borough_data, patch_artist=True)
ax.set_xticks(range(1, len(boroughs) + 1))
ax.set_xticklabels(boroughs, rotation=20)
ax.set_title("Price by Borough")
ax.set_xlabel("Neighbourhood Group")
ax.set_ylabel("Price (USD/night)")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "price_by_borough.png", dpi=160)
plt.close(fig)

# 5) Geographic pattern
sample = eda_df.sample(n=min(15000, len(eda_df)), random_state=SEED)
fig, ax = plt.subplots(figsize=(8, 7))
sc = ax.scatter(sample["longitude"], sample["latitude"], c=sample["price"], cmap="viridis", s=7, alpha=0.5)
ax.set_title("Geographic Pattern of Price")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
cbar = fig.colorbar(sc, ax=ax)
cbar.set_label("Price (USD/night)")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "geo_price_scatter.png", dpi=160)
plt.close(fig)

# 6) Borough x room type heatmap of median price
pivot = eda_df.pivot_table(index="neighbourhood_group", columns="room_type", values="price", aggfunc="median")
fig, ax = plt.subplots(figsize=(9, 5))
im2 = ax.imshow(pivot.values, cmap="YlGnBu")
ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(list(pivot.columns), rotation=20)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(list(pivot.index))
ax.set_title("Median Price by Borough and Room Type")
ax.set_xlabel("Room Type")
ax.set_ylabel("Neighbourhood Group")
for i in range(pivot.shape[0]):
    for j in range(pivot.shape[1]):
        val = pivot.values[i, j]
        if pd.notna(val):
            ax.text(j, i, f"{val:.0f}", ha="center", va="center", fontsize=9)
cbar2 = fig.colorbar(im2, ax=ax)
cbar2.set_label("Median Price (USD/night)")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "borough_roomtype_median_price_heatmap.png", dpi=160)
plt.close(fig)

eda_df.to_csv(OUTPUT_DIR / "eda_cleaned.csv", index=False)

# Summary stats for report
q95 = float(df["price"].quantile(0.95))
q99 = float(df["price"].quantile(0.99))
q995 = float(price_cap)
skew = float(df["price"].skew())

corr_price = corr["price"].drop("price").sort_values(key=lambda s: s.abs(), ascending=False)

summary = f"""# EDA Summary (Task 02)

## Target Variable: `price`
- `price` is strongly right-skewed (skewness = {skew:.2f}) with a long tail.
- Key quantiles: 95th={q95:.1f}, 99th={q99:.1f}, 99.5th={q995:.1f}; max remains very high in raw ingested data.
- For Task 03 modelling, consider robust handling of the target (for example log-transform during model training pipeline) and metrics less sensitive to extreme values.

## Most Important Feature Signals
- `room_type` is a major signal with clear median-price separation.
- `neighbourhood_group` also separates price levels, and interaction with `room_type` is strong.
- Geographic coordinates (`latitude`, `longitude`) show clear spatial price structure.
- Review and availability features have weaker linear correlation but may still add non-linear predictive value.

## Relationships and Subgroups
- Manhattan + Entire home/apt forms the highest-price subgroup.
- Shared/private room listings are consistently lower-price, but spread varies by borough.
- Spatial scatter shows clusters of high prices in central/high-demand zones.

## Remaining Data Quality Decisions
- Additional EDA cleaning applied: rows above the 99.5th percentile of `price` were removed for analysis-ready stability (`eda_cleaned.csv`).
- This cleaning was done for EDA/model-readiness only; train/test splitting is still deferred to Task 03.
- No held-out data was created or used.

## Feature Engineering Ideas for Task 04
- Borough x room_type interaction features.
- Spatial features (distance-to-centroid or cluster labels from latitude/longitude).
- Non-linear transforms for skewed predictors.
- Potential robust scaling/winsorization for heavy-tailed numeric variables.

## Top Correlations With Price (absolute)
{corr_price.head(6).to_string()}
"""

(OUTPUT_DIR / "eda_summary.md").write_text(summary, encoding="utf-8")

print("Saved outputs in", OUTPUT_DIR)
