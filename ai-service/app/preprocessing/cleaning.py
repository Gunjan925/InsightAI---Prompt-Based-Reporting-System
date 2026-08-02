# Cleans datasets by handling missing values, duplicates and datatype conversions.
import re
import pandas as pd
import numpy as np

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the given Pandas DataFrame:
    1. Standardizes column headers to lowercase, alphanumeric snake_case.
    2. Drops duplicate records.
    3. Removes completely null rows or columns.
    4. Auto-detects and converts date columns.
    5. Imputes missing numerical values with column medians, and categorical values with 'Unknown'.
    """
    if df.empty:
        return df

    # Create a copy to prevent in-place warnings
    df_clean = df.copy()

    # 1. Clean and normalize column names
    cleaned_columns = []
    for col in df_clean.columns:
        col_str = str(col).strip()
        # Remove special characters, replace spaces with underscores, keep alphanumeric
        col_str = re.sub(r'[^a-zA-Z0-9\s_]', '', col_str)
        col_str = re.sub(r'\s+', '_', col_str).lower()
        if not col_str:
            col_str = "unnamed_column"
        cleaned_columns.append(col_str)

    # Ensure all column names are unique by appending a suffix
    unique_columns = [] # This will store the new unique column names.
    col_tracker = {} # Dictionary to count how many times each column name has appeared.
    for col in cleaned_columns:
        if col in col_tracker:
            col_tracker[col] += 1
            unique_columns.append(f"{col}_{col_tracker[col]}") # example if sales for 2nd time then sales_2
        else:
            col_tracker[col] = 0
            unique_columns.append(col)
    df_clean.columns = unique_columns

    # 2. Remove entirely empty rows and columns
    df_clean.dropna(how="all", inplace=True) # rows
    df_clean.dropna(how="all", axis=1, inplace=True) # cols

    # 3. Remove duplicate records
    df_clean.drop_duplicates(inplace=True)

    # 4. Attempt to detect and parse datetime columns : automatically detects columns that contain dates stored as text and converts them into proper Pandas datetime columns.
    for col in df_clean.columns:
        if df_clean[col].dtype == "object":
            # Test a sample of non-null values to verify if they represent dates
            sample_non_null = df_clean[col].dropna().head(10) # Takes the first 10 non-empty values as a sample.
            if len(sample_non_null) > 0:
                try:
                    # Attempts to convert the sample into dates. Valid dates → converted successfully. Invalid values → become NaT (Not a Time).
                    parsed_sample = pd.to_datetime(sample_non_null, errors="coerce")
                    # If 80% or more of non-null rows parse successfully, convert the column
                    # Checks how many sample values were successfully converted. notna() → True for valid dates, False for invalid ones mean() on booleans gives the percentage of True values.
                    if parsed_sample.notna().mean() >= 0.8:
                        df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce")
                except Exception:
                    pass # If conversion fails for any reason, the program ignores the error and continues with the next column.

    # 5. Impute missing values
    for col in df_clean.columns:
        # Numeric column imputation
        if np.issubdtype(df_clean[col].dtype, np.number): # Checks if the column contains numbers (int, float, etc.).
            if df_clean[col].isnull().any():
                col_median = df_clean[col].median()
                # If median itself is NaN (all values null), fallback to 0
                if pd.isnull(col_median):
                    col_median = 0
                df_clean[col] = df_clean[col].fillna(col_median)
                
        # Datetime column imputation
        elif np.issubdtype(df_clean[col].dtype, np.datetime64) or isinstance(df_clean[col].dtype, pd.DatetimeTZDtype): # Checks if the column contains dates.
            if df_clean[col].isnull().any():
                # Forward/backward fill temporal gaps
                df_clean[col] = df_clean[col].ffill().bfill() # Copies the previous valid date. If the missing value is at the beginning, it uses the next valid date.
                # If still null (entire column missing dates), default to epoch
                if df_clean[col].isnull().any():
                    df_clean[col] = df_clean[col].fillna(pd.Timestamp("1970-01-01"))
                    
        # Categorical/Object column imputation
        else:
            if df_clean[col].isnull().any():
                df_clean[col] = df_clean[col].fillna("Unknown")

    return df_clean