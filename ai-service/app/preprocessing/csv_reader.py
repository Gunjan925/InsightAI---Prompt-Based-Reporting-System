# Reads CSV datasets into Pandas DataFrames.
import io
import pandas as pd
from app.exceptions.custom_exception import DatasetProcessingError

def read_csv(file_bytes: bytes) -> pd.DataFrame:
    """
    Reads a CSV dataset from raw bytes into a Pandas DataFrame.
    Includes simple separator auto-detection (comma, semicolon, or tab).
    """
    try:
        # Decode a small sample to analyze headers and separators
        sample = file_bytes[:4096].decode("utf-8", errors="ignore") # Takes only the first 4096 bytes. Decodes them into text. Used only to determine the delimiter.
        
        # Heuristic detection for common CSV delimiters
        delimiter = ","
        if len(sample) > 0:
            comma_count = sample.count(",")
            semicolon_count = sample.count(";")
            tab_count = sample.count("\t")
            
            if semicolon_count > comma_count and semicolon_count > tab_count:
                delimiter = ";"
            elif tab_count > comma_count and tab_count > semicolon_count:
                delimiter = "\t"
                
        # Parse byte stream into DataFrame
        # BytesIO(file_bytes) converts the bytes into a file-like object. pd.read_csv() reads it using the detected delimiter.
        df = pd.read_csv(io.BytesIO(file_bytes), sep=delimiter)
        
        if df.empty:
            raise DatasetProcessingError("The uploaded CSV file is empty.")
            
        return df
    except DatasetProcessingError:
        raise
    except Exception as e:
        raise DatasetProcessingError(f"Failed to parse CSV dataset: {str(e)}")