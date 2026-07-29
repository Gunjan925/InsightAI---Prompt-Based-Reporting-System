from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict

# If the input is an object, read its attributes (user.id, user.username, etc.) instead of expecting a dictionary.
class ReportGenerateRequest(BaseModel):
    file_id: int = Field(..., description="ID of the uploaded dataset file to analyze")
    prompt: str = Field(..., min_length=5, description="Prompt specifying report instructions or analysis type")

class ReportResponse(BaseModel):
    id: int
    user_id: int
    file_id: int
    prompt: str
    report_title: str
    summary: Optional[str] = None
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ReportListItem(BaseModel):
    id: int
    file_id: int
    filename: str
    report_title: str
    summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_files_uploaded: int
    total_reports_generated: int
    latest_report_title: Optional[str] = None
    latest_report_date: Optional[datetime] = None
    file_type_distribution: Dict[str, int]