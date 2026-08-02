# Reads Excel datasets into Pandas DataFrames.
import io
import pandas as pd
from app.exceptions.custom_exception import DatasetProcessingError

def read_excel(file_bytes: bytes) -> pd.DataFrame:
    """
    Reads an Excel dataset (.xls, .xlsx) from binary bytes into a Pandas DataFrame.
    By default, it parses the first sheet of the workbook.
    """
    try:
        # Use openpyxl engine to parse Excel from bytes in memory
        df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
        
        if df.empty:
            raise DatasetProcessingError("The uploaded Excel sheet contains no data.")
            
        return df
    except DatasetProcessingError:
        raise
    except Exception as e:
        raise DatasetProcessingError(f"Failed to parse Excel dataset: {str(e)}")