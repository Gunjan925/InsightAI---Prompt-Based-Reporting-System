# Defines the structure of API responses returned to the backend.
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class HealthResponse(BaseModel):
    """
    Standard schema for service health status endpoints.
    """
    status: str = Field(default="ok", description="Service operation status code")
    version: str = Field(default="1.0.0", description="Microservice codebase release version")

class ChartConfigResponse(BaseModel):
    """
    Defines the metadata configuration for recommended Plotly visualizations.
    """
    type: str = Field(..., description="Visual chart type (bar, line, scatter, pie, heatmap, histogram)")
    title: str = Field(..., description="Graph title description")
    description: str = Field(..., description="Short explanation highlighting visual trends")
    x: Optional[str] = Field(default=None, description="Column name for X axis")
    y: Optional[str] = Field(default=None, description="Column name for Y axis")
    category: Optional[str] = Field(default=None, description="Categorical column name for grouping/pie slices")
    plotly_json: str = Field(..., description="Full Plotly Figure configuration serialized to a JSON string")

class DashboardResponse(BaseModel):
    """
    Structure of initial dashboard profiles and charts returned to the backend.
    """
    dataset_id: str = Field(..., description="Target dataset reference key")
    row_count: int = Field(..., description="Total row dimensions count")
    col_count: int = Field(..., description="Total column dimensions count")
    columns: Dict[str, Any] = Field(..., description="Column headers mapping data types and null counts")
    charts: List[ChartConfigResponse] = Field(..., description="List of auto-generated Plotly chart recommendations")

class ChatResponse(BaseModel):
    """
    Holds LLM response content and the semantically retrieved dataset context.
    """
    response: str = Field(..., description="LLM text answer response explaining insights")
    retrieved_context: List[Dict[str, Any]] = Field(..., description="List of row-level data segments retrieved from vector search")

class ReportResponse(BaseModel):
    """
    Standard format returned upon compilation requests.
    """
    report_title: str = Field(..., description="Generated report title")
    summary: str = Field(..., description="Brief paragraph summary of insights")
    content: str = Field(..., description="Complete interactive single-page HTML report document content")
    statistics: Dict[str, Any] = Field(..., description="Full statistical profiling metrics dictionary")
    charts: List[ChartConfigResponse] = Field(..., description="List of Plotly charts attached within report layout")