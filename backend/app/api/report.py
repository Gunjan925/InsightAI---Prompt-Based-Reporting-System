from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.report_schema import ReportGenerateRequest, ReportResponse
from app.controllers.report_controller import ReportController
from app.middlewares.auth import get_current_user
from app.models.user import User

# Creates a group of related API endpoints. Adds /report before every endpoint (/report/generate). Groups these APIs under Reports in Swagger UI.
# Swagger UI is an automatically generated interactive webpage that documents all your FastAPI APIs. It lets you view, test, and understand your endpoints without using tools like Postman. Swagger UI: http://127.0.0.1:8000/docs — Interactive documentation where you can test APIs.
router = APIRouter(prefix="/report", tags=["Reports"])

@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(request: ReportGenerateRequest,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    """
    Generate an intelligent AI report using an uploaded dataset and customized prompt.
    The request is forwarded to the AI service, and the returned report is stored locally.
    """
    return await ReportController.generate_report(db, request, current_user.id)

@router.get("/{report_id}", response_model=ReportResponse, status_code=status.HTTP_200_OK)
def get_report(report_id: int,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    """
    Retrieve report summary, metadata, and full HTML analysis content.
    """
    return ReportController.get_report(db, report_id, current_user.id)

@router.get("/{report_id}/download", status_code=status.HTTP_200_OK)
def download_report(report_id: int,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    """
    Download the generated report as an interactive HTML document.
    """
    report = ReportController.get_report(db, report_id, current_user.id)

    # Content-Disposition is an HTTP response header that tells the browser what to do with the response body. 
    # "Content-Disposition": "attachment" -> the browser thinks: "The server wants me to download this file." Instead of opening it, it immediately starts downloading.
    # filename=report_{report_id}.html -> This tells the browser: "When you save this file, use this name."
    # f"attachment; filename=report_{report_id}.html" becomes attachment; filename=report_15.html -> Now browser downloads report_15.html instead of download.html or index.html
    headers = {
        "Content-Disposition": f"attachment; filename=report_{report_id}.html"
    }
    # This creates and sends the complete HTTP response back to the client. Return the report content as an HTML response with download headers
    return Response(content=report.content, media_type="text/html", headers=headers)

# complete workflow for the download_report function : 
'''
User clicks
"Download Report"

        │
        ▼

Backend creates

Response(
    content=HTML Report,
    media_type="text/html",
    headers={
        "Content-Disposition":
        "attachment; filename=report_15.html"
    }
)

        │
        ▼

Browser receives response

        │
        ▼

Reads Content-Type
→ HTML file

Reads Content-Disposition
→ Download instead of display

        │
        ▼

Downloads

report_15.html
'''