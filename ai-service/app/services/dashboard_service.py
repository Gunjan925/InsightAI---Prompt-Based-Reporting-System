# Coordinates preprocessing, statistics and automatic dashboard chart generation.
import os
import logging
import pandas as pd
from app.preprocessing.csv_reader import read_csv
from app.preprocessing.excel_reader import read_excel
from app.preprocessing.cleaning import clean_dataframe
from app.preprocessing.statistics import compute_statistics
from app.visualization.chart_selector import select_recommended_charts
from app.visualization.charts import generate_plotly_chart
from app.exceptions.custom_exception import DatasetProcessingError

logger = logging.getLogger("ai_service")

class DashboardService:
    """
    Coordinates dataset ingestion, cleaning, metrics calculations,
    and automatic chart creation (independent of LLM).
    """
    @staticmethod
    def process_dataset(filename: str, file_bytes: bytes) -> dict:
        """
        Reads, cleans, profiles, and recommends visual charts for a dataset file.
        Returns dashboard metrics and serialized chart JSON configs.
        """
        # Determine file type
        _, ext = os.path.splitext(filename.lower())
        logger.info(f"Processing dataset '{filename}' (type: {ext})")

        try:
            # 1. Parse dataset into Pandas DataFrame
            if ext == ".csv":
                df = read_csv(file_bytes)
            elif ext in (".xls", ".xlsx"):
                df = read_excel(file_bytes)
            else:
                raise DatasetProcessingError(f"Unsupported dataset format '{ext}'. Must be CSV or Excel.")

            # 2. Preprocess and clean the DataFrame
            cleaned_df = clean_dataframe(df)
            logger.info(f"Dataset cleaned. Dimensions: {cleaned_df.shape[0]} rows, {cleaned_df.shape[1]} columns.")

            # 3. Calculate descriptive statistics
            stats = compute_statistics(cleaned_df)

            # 4. Recommend visual charts
            chart_configs = select_recommended_charts(stats)
            logger.info(f"Recommender suggested {len(chart_configs)} chart visualizations.")

            # 5. Generate interactive Plotly JSON configs for each recommendation
            generated_charts = []
            for config in chart_configs:
                plotly_json = generate_plotly_chart(cleaned_df, config)
                generated_charts.append({
                    "type": config.get("type"),
                    "title": config.get("title"),
                    "description": config.get("description"),
                    "x": config.get("x"),
                    "y": config.get("y"),
                    "category": config.get("category"),
                    "plotly_json": plotly_json
                })

            return {
                "dataset_id": filename,
                "row_count": stats.get("shape", [0, 0])[0],
                "col_count": stats.get("shape", [0, 0])[1],
                "columns": stats.get("columns", {}),
                "charts": generated_charts,
                "statistics": stats,          # Store in cache or pass downstream
                "cleaned_df": cleaned_df       # Retained for downstream RAG vector updates
            }

        except DatasetProcessingError:
            raise
        except Exception as e:
            logger.error(f"Error in DashboardService dataset pipeline: {e}")
            raise DatasetProcessingError(f"Dataset processing workflow failed: {str(e)}")