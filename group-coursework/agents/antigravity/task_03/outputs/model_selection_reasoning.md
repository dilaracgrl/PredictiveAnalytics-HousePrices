# Model Selection Reasoning

Based on the EDA from Task 02, we discovered two key facts:
1. `price` is massively right-skewed. Regressing on it directly causes MSE optimization to hyper-focus on extreme upper-tail errors.
2. Numeric variables (reviews, availability) are weak linear predictors, while categorical location (`neighbourhood_group`) and `room_type` determine subgroups with massive price variance.

**Baseline Choice:** `Ridge Regression`.
- **Why:** Using an L2-regularized linear model allows us to utilize One-Hot Encoding on categorical features without breaking down via perfect multicollinearity. It handles high-dimensionality well and provides a strong linear floor.
- **Target Transformation:** We will use `TransformedTargetRegressor` passing `np.log1p` during fit and `np.expm1` during predict. This bounds the heteroskedasticity while handling inference entirely transparently.
- **Limitations:** A linear baseline won't capture complex non-linear combinations (e.g., specific interactions between coordinates and room limits), providing clear runway for Task 04 to improve via tree-based models.