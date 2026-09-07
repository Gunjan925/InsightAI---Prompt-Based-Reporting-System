# Generates Plotly figures and returns them in memory (JSON or bytes), without saving image files.
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json

# Curated modern colors matching premium UI design (indigo, teal, rose, and amber)
PRIMARY_COLOR = "#4f46e5"
SECONDARY_COLOR = "#0284c7"
ACCENT_COLOR = "#e11d48"
PALETTE = [PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, "#d97706", "#7c3aed", "#059669", "#06b6d4"]

def _clean_label(col_name: str) -> str:
    """Helper to convert column names (e.g. 'total_sales_usd') to intuitive title case ('Total Sales Usd')."""
    if not col_name:
        return ""
    return str(col_name).replace("_", " ").strip().title()

def generate_plotly_chart(df: pd.DataFrame, config: dict) -> str:
    """
    Generates a Plotly visualization based on dataset values and chart configuration rules.
    Returns the plotly figure serialized as a JSON string to be rendered directly on the frontend.
    """
    if df.empty:
        return json.dumps({})

    chart_type = config.get("type", "histogram")
    title = config.get("title", "")

    # Common styling theme with clear, intuitive labels and visible gridlines
    layout_theme = {
        "title": {
            "text": title,
            "font": {"family": "Outfit, Inter, system-ui, sans-serif", "size": 15, "color": "#1e293b"},
            "x": 0.02,
            "y": 0.96
        },
        "font": {"family": "Inter, system-ui, sans-serif", "color": "#334155"},
        "paper_bgcolor": "#ffffff",
        "plot_bgcolor": "#f8fafc",
        "margin": {"l": 55, "r": 25, "t": 55, "b": 55},
        "xaxis": {
            "gridcolor": "#e2e8f0",
            "linecolor": "#cbd5e1",
            "zeroline": False,
            "automargin": True,
            "tickfont": {"size": 11, "color": "#334155"}
        },
        "yaxis": {
            "gridcolor": "#e2e8f0",
            "linecolor": "#cbd5e1",
            "zeroline": False,
            "automargin": True,
            "tickfont": {"size": 11, "color": "#334155"}
        },
        "hovermode": "closest",
        "legend": {
            "font": {"size": 11, "color": "#334155"},
            "orientation": "h",
            "y": -0.2
        }
    }

    try:
        fig = None

        if chart_type == "line":
            x_col = config.get("x")
            y_col = config.get("y")
            clean_x = _clean_label(x_col)
            clean_y = _clean_label(y_col)
            
            # Aggregation to handle duplicate dates/times
            agg_df = df.groupby(x_col)[y_col].mean().reset_index()
            agg_df = agg_df.sort_values(by=x_col)
            
            fig = px.line(agg_df, x=x_col, y=y_col, color_discrete_sequence=[PRIMARY_COLOR])
            # Enable both lines and markers so data plot points are clearly visible
            fig.update_traces(
                mode="lines+markers",
                line=dict(width=3),
                marker=dict(size=7, symbol="circle", line=dict(width=1.5, color="#ffffff"))
            )
            layout_theme["xaxis"]["title"] = {"text": clean_x, "font": {"size": 12, "color": "#1e293b", "family": "Inter"}}
            layout_theme["yaxis"]["title"] = {"text": f"Average {clean_y}", "font": {"size": 12, "color": "#1e293b", "family": "Inter"}}
            if not title:
                layout_theme["title"]["text"] = f"Trend Analysis: {clean_y} over {clean_x}"

        elif chart_type == "bar":
            x_col = config.get("x")
            y_col = config.get("y")
            clean_x = _clean_label(x_col)
            clean_y = _clean_label(y_col)
            
            # Group by and aggregate to find averages across groups
            agg_df = df.groupby(x_col)[y_col].mean().reset_index()
            agg_df = agg_df.sort_values(by=y_col, ascending=False).head(12)
            
            fig = px.bar(agg_df, x=x_col, y=y_col, color_discrete_sequence=[PRIMARY_COLOR])
            # Show value labels on bar ends so markings are easily visible
            fig.update_traces(
                marker_line_width=1,
                marker_line_color="#3730a3",
                opacity=0.9,
                texttemplate='%{y:.2s}',
                textposition='auto'
            )
            layout_theme["xaxis"]["title"] = {"text": clean_x, "font": {"size": 12, "color": "#1e293b"}}
            layout_theme["yaxis"]["title"] = {"text": f"Average {clean_y}", "font": {"size": 12, "color": "#1e293b"}}
            layout_theme["xaxis"]["tickangle"] = -35
            if not title:
                layout_theme["title"]["text"] = f"{clean_y} Breakdown by {clean_x}"

        elif chart_type == "pie":
            cat_col = config.get("category")
            clean_cat = _clean_label(cat_col)
            agg_df = df[cat_col].value_counts().reset_index()
            agg_df.columns = [cat_col, "count"]
            
            # Create interactive donut chart with clear labels & percentages
            fig = px.pie(agg_df, names=cat_col, values="count", color_discrete_sequence=PALETTE, hole=0.35)
            fig.update_traces(
                textposition="inside",
                textinfo="label+percent",
                marker=dict(line=dict(color="#ffffff", width=2))
            )
            layout_theme["annotations"] = [{
                "text": clean_cat,
                "x": 0.5,
                "y": 0.5,
                "font_size": 13,
                "showarrow": False,
                "font_color": "#334155",
                "font_family": "Inter"
            }]
            if not title:
                layout_theme["title"]["text"] = f"Proportional Share: {clean_cat}"

        elif chart_type == "scatter":
            x_col = config.get("x")
            y_col = config.get("y")
            clean_x = _clean_label(x_col)
            clean_y = _clean_label(y_col)
            fig = px.scatter(df, x=x_col, y=y_col, color_discrete_sequence=[SECONDARY_COLOR])
            fig.update_traces(marker=dict(size=8, opacity=0.8, line=dict(width=1.5, color="#ffffff")))
            layout_theme["xaxis"]["title"] = {"text": clean_x, "font": {"size": 12, "color": "#1e293b"}}
            layout_theme["yaxis"]["title"] = {"text": clean_y, "font": {"size": 12, "color": "#1e293b"}}
            if not title:
                layout_theme["title"]["text"] = f"Correlation: {clean_x} vs {clean_y}"

        elif chart_type == "histogram":
            x_col = config.get("x")
            clean_x = _clean_label(x_col)
            fig = px.histogram(df, x=x_col, color_discrete_sequence=[PRIMARY_COLOR])
            fig.update_traces(marker_line_width=1, marker_line_color="#312e81", opacity=0.85)
            layout_theme["xaxis"]["title"] = {"text": clean_x, "font": {"size": 12, "color": "#1e293b"}}
            layout_theme["yaxis"]["title"] = {"text": "Frequency (Count)", "font": {"size": 12, "color": "#1e293b"}}
            if not title:
                layout_theme["title"]["text"] = f"Distribution Spread of {clean_x}"

        elif chart_type == "heatmap":
            numerical_df = df.select_dtypes(include=[np.number])
            if len(numerical_df.columns) >= 2:
                corr = numerical_df.corr().round(2)
                clean_cols = [_clean_label(c) for c in corr.columns]
                fig = go.Figure(data=go.Heatmap(
                    z=corr.values,
                    x=clean_cols,
                    y=clean_cols,
                    colorscale="Blues",
                    zmin=-1, zmax=1,
                    text=corr.values,
                    texttemplate="%{text}",
                    textfont={"size": 11, "color": "#0f172a"},
                    hoverongaps=False
                ))
                layout_theme["xaxis"]["title"] = {"text": "Numerical Features", "font": {"size": 12, "color": "#1e293b"}}
                layout_theme["yaxis"]["title"] = {"text": "Numerical Features", "font": {"size": 12, "color": "#1e293b"}}
                layout_theme["xaxis"]["tickangle"] = -35
                layout_theme["yaxis"]["tickangle"] = 0
                if not title:
                    layout_theme["title"]["text"] = "Numerical Features Correlation Matrix"
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
            title=f"Chart Generation Error: {str(e)}",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#f8fafc"
        )
        return error_fig.to_json()