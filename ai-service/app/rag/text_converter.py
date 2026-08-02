# Converts tabular data into textual chunks suitable for embedding.
import pandas as pd

def convert_dataframe_to_text_chunks(df: pd.DataFrame) -> list[dict]:
    """
    Converts a Pandas DataFrame into a list of descriptive text blocks.
    Generates:
    1. A text block for each row summarizing all values and column titles.
    2. A schema text block summarizing column names and data types to handle meta-queries.
    Each chunk is mapped to a dict with 'text' and 'metadata'.
    """
    chunks = [] # Every row will become one chunk.
    columns = df.columns.tolist() # Gets all column names.

    # 1. Generate descriptive text blocks for each row
    for idx, row in df.iterrows(): # Loops over every row.
        row_elements = [f"Row {idx + 1}:"] # Creates the beginning of the sentence.
        for col in columns:
            val = row[col]
            if pd.isnull(val):
                val_str = "None"
            elif isinstance(val, pd.Timestamp):
                val_str = val.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(val, float):
                # Format float values up to 4 decimals, trim trailing zeros
                val_str = f"{val:.4f}".rstrip('0').rstrip('.')
            else:
                val_str = str(val)
            row_elements.append(f"'{col}' is '{val_str}'")
            
        text_block = ", ".join(row_elements)
        chunks.append({
            "text": text_block,
            "metadata": {
                "row_index": int(idx),
                "type": "row"
            }
        })

    # 2. Generate a high-level dataset schema block
    schema_elements = ["Dataset Structure Overview:"]
    for col in columns:
        dtype_str = str(df[col].dtype)
        schema_elements.append(f"Column '{col}' of type {dtype_str}")
    schema_text = ". ".join(schema_elements)
    
    chunks.append({
        "text": schema_text,
        "metadata": {
            "row_index": -1,
            "type": "schema"
        }
    })

    return chunks