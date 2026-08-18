# Determines the most suitable charts based on dataset column types.
import pandas as pd
import numpy as np

def select_recommended_charts(stats: dict) -> list:
    """
    Selects a list of recommended chart configurations based on the dataset summary statistics:
    - Time Series Line Chart: generated if datetime and numerical columns are present.
    - Pie Chart: recommended for categorical columns with 8 or fewer unique classes.
    - Bar Chart: maps categorical segments against numerical aggregates.
    - Scatter Plot: shows the relationship between two primary numerical variables.
    - Correlation Heatmap: maps pairwise correlation across numerical columns.
    - Histogram: maps numerical frequencies to check distributions.
    """
    recommendations = []
    numerical_cols = stats.get("numerical_columns", [])
    categorical_cols = stats.get("categorical_columns", [])
    datetime_cols = stats.get("datetime_columns", [])

    # 1. Temporal Trend Line Chart
    if datetime_cols and numerical_cols:
        date_col = datetime_cols[0]
        # Recommend line charts for up to 3 numerical columns
        for num_col in numerical_cols[:3]:
            recommendations.append({
                "type": "line",
                "x": date_col,
                "y": num_col,
                "title": f"Trend of {num_col} over {date_col}",
                "description": f"Displays temporal changes, spikes, or seasonality in {num_col} across timeline."
            })

    # 2. Categorical Comparison (Bar & Pie Charts)
    if categorical_cols and numerical_cols:
        # Loop over up to 3 categorical columns
        for cat_col in categorical_cols[:3]:
            num_col = numerical_cols[0]
            
            # Pie chart is recommended only for low-cardinality categorical variables
            unique_categories = stats.get("categorical_stats", {}).get(cat_col, {}).get("unique_count", 0)
            if 2 <= unique_categories <= 8:
                recommendations.append({
                    "type": "pie",
                    "category": cat_col,
                    "title": f"Share Distribution by {cat_col}",
                    "description": f"Visualizes proportional breakdown and composition of {cat_col} items."
                })
                
            recommendations.append({
                "type": "bar",
                "x": cat_col,
                "y": num_col,
                "title": f"Average {num_col} across {cat_col}",
                "description": f"Compares how numerical {num_col} varies across categorical groups of {cat_col}."
            })

    # 3. Correlation & Relationship (Scatter & Heatmap Charts)
    if len(numerical_cols) >= 2:
        # Recommend scatter plots for up to 3 different pairs of numerical columns
        pairs = [(numerical_cols[i], numerical_cols[j]) for i in range(len(numerical_cols)) for j in range(i+1, len(numerical_cols))]
        for num1, num2 in pairs[:3]:
            recommendations.append({
                "type": "scatter",
                "x": num1,
                "y": num2,
                "title": f"Relationship: {num1} vs {num2}",
                "description": f"Scatter plot mapping correlation, clusters, or outlier points between {num1} and {num2}."
            })
        
        # Always recommend correlation heatmap if 2+ numeric columns exist
        recommendations.append({
            "type": "heatmap",
            "title": "Numerical Correlation Coefficients",
            "description": "Heatmap illustrating the direction and strength of linear correlations between metrics."
        })

    # 4. Univariate Numerical Distribution (Histogram)
    if numerical_cols:
        # Recommend histograms for up to 3 numerical columns
        for num_col in numerical_cols[:3]:
            recommendations.append({
                "type": "histogram",
                "x": num_col,
                "title": f"Frequency Spread of {num_col}",
                "description": f"Bar histogram detailing frequency grouping and data distribution shape for {num_col}."
            })

    # Fallback default values
    if not recommendations:
        if numerical_cols:
            recommendations.append({
                "type": "histogram",
                "x": numerical_cols[0],
                "title": f"Distribution of {numerical_cols[0]}",
                "description": "Statistical frequency distribution graph."
            })
        elif categorical_cols:
            recommendations.append({
                "type": "bar",
                "x": categorical_cols[0],
                "title": f"Records Distribution by {categorical_cols[0]}",
                "description": "Category counts summary chart."
            })

    return recommendations