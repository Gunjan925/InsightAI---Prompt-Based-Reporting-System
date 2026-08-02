# Combines statistics, dashboard charts and AI insights into a unified report structure.
import logging
from app.report.html_generator import generate_report_html
from app.report.pdf_generator import generate_report_pdf

logger = logging.getLogger("ai_service")

def compile_report(dataset_id: str, stats: dict, charts: list[dict], ai_insights: dict) -> dict:
    """
    Compiles data preprocessing statistics, recommended charts (with Plotly JSON configs),
    and Gemini LLM insights into a unified dictionary structure.
    Generates and attaches the final HTML report content string.
    """
    title = ai_insights.get("report_title", f"InsightAI Analysis Report - {dataset_id}")
    summary = ai_insights.get("summary", "AI generated statistical analysis report.")
    ai_html = ai_insights.get("content", "<h1>No content generated</h1>")

    # Generate the complete interactive HTML report
    html_content = generate_report_html(
        title=title,
        dataset_id=dataset_id,
        row_count=stats.get("shape", [0, 0])[0],
        col_count=stats.get("shape", [0, 0])[1],
        columns=stats.get("columns", {}),
        charts=charts,
        ai_analysis_html=ai_html
    )

    logger.info("Report components compiled successfully into unified dictionary payload.")

    return {
        "report_title": title,
        "summary": summary,
        "content": html_content,
        "statistics": stats,
        "charts": charts
    }