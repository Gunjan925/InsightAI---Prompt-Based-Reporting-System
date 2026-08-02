# Computes descriptive statistics, correlations and dataset summaries.
import pandas as pd
import numpy as np

def compute_statistics(df: pd.DataFrame) -> dict:
    """
    Computes statistical profiles and metadata summary of a Pandas DataFrame:
    1. Returns dimensions (shape) and lists of column groups by type.
    2. Column-by-column missing value calculations.
    3. Descriptive metrics for numerical features (mean, median, standard deviation, q1, q3, outliers count).
    4. Unique value counts and top category distributions for categorical variables.
    5. Pearson correlation matrix for numerical columns.
    6. Minimum and maximum timestamp bounds for datetime columns.
    """
    if df.empty:
        return {}

    total_rows = len(df)
    total_cols = len(df.columns)

    # Classify columns based on data types
    numerical_cols = []
    categorical_cols = []
    datetime_cols = []

    for col in df.columns:
        if np.issubdtype(df[col].dtype, np.number):
            numerical_cols.append(col)
        elif np.issubdtype(df[col].dtype, np.datetime64) or isinstance(df[col].dtype, pd.DatetimeTZDtype):
            datetime_cols.append(col)
        else:
            categorical_cols.append(col)

    # 1. General column details (type, missing value counts)
    column_metadata = {}
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        column_metadata[col] = {
            "type": str(df[col].dtype),
            "null_count": null_count,
            "null_percentage": float((null_count / total_rows) * 100) if total_rows > 0 else 0.0
        }

    # 2. Descriptive statistics for numerical columns
    numerical_stats = {}
    for col in numerical_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue
            
        # Outlier counts based on Interquartile Range (IQR)
        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers_count = int(((series < lower_bound) | (series > upper_bound)).sum())

        numerical_stats[col] = {
            "mean": float(series.mean()),
            "median": float(series.median()),
            "min": float(series.min()),
            "max": float(series.max()),
            "std": float(series.std()) if len(series) > 1 else 0.0,
            "q1": q1,
            "q3": q3,
            "outliers_count": outliers_count
        }

    # 3. Categorical distribution summaries
    categorical_stats = {}
    for col in categorical_cols:
        value_distribution = {}
        top_categories = df[col].value_counts().head(10)
        for val, count in top_categories.items():
            value_distribution[str(val)] = {
                "count": int(count),
                "percentage": float((count / total_rows) * 100) if total_rows > 0 else 0.0
            }
        categorical_stats[col] = {
            "unique_count": int(df[col].nunique()),
            "top_categories": value_distribution
        }

    # 4. Correlation matrix for numerical fields
    correlations = {}
    if len(numerical_cols) > 1:
        corr_matrix = df[numerical_cols].corr()
        # Replace NaN values with None for JSON standard compatibility
        corr_matrix = corr_matrix.replace({np.nan: None})
        for col_a in corr_matrix.index:
            correlations[col_a] = {}
            for col_b in corr_matrix.columns:
                val = corr_matrix.loc[col_a, col_b]
                correlations[col_a][col_b] = float(val) if val is not None else None

    # 5. Temporal ranges for date fields
    temporal_stats = {}
    for col in datetime_cols:
        series = df[col].dropna()
        if len(series) > 0:
            temporal_stats[col] = {
                "min": str(series.min()),
                "max": str(series.max())
            }

    return {
        "shape": [total_rows, total_cols],
        "columns": column_metadata,
        "numerical_columns": numerical_cols,
        "categorical_columns": categorical_cols,
        "datetime_columns": datetime_cols,
        "numerical_stats": numerical_stats,
        "categorical_stats": categorical_stats,
        "correlations": correlations,
        "temporal_stats": temporal_stats
    }