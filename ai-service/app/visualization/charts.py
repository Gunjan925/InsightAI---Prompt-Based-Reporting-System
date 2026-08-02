# Generates Plotly figures and returns them in memory (JSON or bytes), without saving image files.
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json

# Curated modern colors matching premium UI design (indigo, teal, rose, and amber)
PRIMARY_COLOR = "#6366f1"
SECONDARY_COLOR = "#06b6d4"
ACCENT_COLOR = "#ec4899"
PALETTE = [PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, "#f59e0b", "#8b5cf6", "#10b981"]

def generate_plotly_chart(df: pd.DataFrame, config: dict) -> str:
    """
    Generates a Plotly visualization based on dataset values and chart configuration rules.
    Returns the plotly figure serialized as a JSON string to be rendered directly on the frontend.
    """
    if df.empty:
        return json.dumps({})

    chart_type = config.get("type", "histogram")
    title = config.get("title", "")

    # Common styling theme mapping rich visual aesthetics
    layout_theme = {
        "title": {
            "text": title,
            "font": {"family": "Outfit, Inter, system-ui, sans-serif", "size": 16, "color": "#1f2937"},
            "x": 0.05,
            "y": 0.95
        },
        "font": {"family": "Inter, system-ui, sans-serif", "color": "#4b5563"},
        "paper_bgcolor": "rgba(255, 255, 255, 0.95)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "margin": {"l": 50, "r": 30, "t": 65, "b": 50},
        "xaxis": {
            "gridcolor": "#f3f4f6",
            "linecolor": "#e5e7eb",
            "zeroline": False,
            "tickfont": {"size": 11}
        },
        "yaxis": {
            "gridcolor": "#f3f4f6",
            "linecolor": "#e5e7eb",
            "zeroline": False,
            "tickfont": {"size": 11}
        },
        "hovermode": "closest"
    }

    try:
        fig = None

        if chart_type == "line":
            x_col = config.get("x")
            y_col = config.get("y")
            # Aggregation to handle duplicate dates/times
            agg_df = df.groupby(x_col)[y_col].mean().reset_index()
            agg_df = agg_df.sort_values(by=x_col)
            
            fig = px.line(agg_df, x=x_col, y=y_col, color_discrete_sequence=[PRIMARY_COLOR])
            fig.update_traces(line=dict(width=3), marker=dict(size=6, symbol="circle"))

        elif chart_type == "bar":
            x_col = config.get("x")
            y_col = config.get("y")
            # Group by and aggregate to find averages across groups
            agg_df = df.groupby(x_col)[y_col].mean().reset_index()
            # Sort and take top 15 values for visual readability
            agg_df = agg_df.sort_values(by=y_col, ascending=False).head(15)
            
            fig = px.bar(agg_df, x=x_col, y=y_col, color_discrete_sequence=[PRIMARY_COLOR])
            fig.update_traces(marker_line_width=0, opacity=0.85)

        elif chart_type == "pie":
            cat_col = config.get("category")
            agg_df = df[cat_col].value_counts().reset_index()
            agg_df.columns = [cat_col, "count"]
            
            # Create interactive donut chart
            fig = px.pie(agg_df, names=cat_col, values="count", color_discrete_sequence=PALETTE, hole=0.4)
            fig.update_traces(textposition="inside", textinfo="percent+label")

        elif chart_type == "scatter":
            x_col = config.get("x")
            y_col = config.get("y")
            fig = px.scatter(df, x=x_col, y=y_col, color_discrete_sequence=[SECONDARY_COLOR])
            fig.update_traces(marker=dict(size=8, opacity=0.75, line=dict(width=1, color="white")))

        elif chart_type == "histogram":
            x_col = config.get("x")
            fig = px.histogram(df, x=x_col, color_discrete_sequence=[PRIMARY_COLOR])
            fig.update_traces(marker_line_width=0.5, opacity=0.8)

        elif chart_type == "heatmap":
            numerical_df = df.select_dtypes(include=[np.number])
            if len(numerical_df.columns) >= 2:
                corr = numerical_df.corr().round(3)
                fig = go.Figure(data=go.Heatmap(
                    z=corr.values,
                    x=corr.columns,
                    y=corr.columns,
                    colorscale="Blues",
                    zmin=-1, zmax=1,
                    hoverongaps=False
                ))
                layout_theme["yaxis"]["tickangle"] = -45
            else:
                fig = go.Figure()

        if fig is None:
            fig = px.histogram(df, x=df.columns[0], color_discrete_sequence=[PRIMARY_COLOR])

        # Apply visual styles
        fig.update_layout(**layout_theme)
        return fig.to_json()

    except Exception as e:
        error_fig = go.Figure()
        error_fig.update_layout(
            title=f"Chart Generation Failed: {str(e)}",
            paper_bgcolor="rgba(255, 255, 255, 0.95)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return error_fig.to_json()