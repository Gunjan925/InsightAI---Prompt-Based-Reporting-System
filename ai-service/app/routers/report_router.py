# API endpoints for generating PDF or HTML reports.
from fastapi import APIRouter, UploadFile, File, Form, status
from app.services.report_service import ReportService
from app.schemas.response_schema import ReportResponse

# Setup router for report generation endpoints
router = APIRouter(tags=["Reports"])

# Function to generate the report
@router.post("/api/generate", response_model=ReportResponse, status_code=status.HTTP_200_OK)
async def generate_report(
    file: UploadFile = File(...),
    prompt: str = Form(...)
) -> ReportResponse:
    """
    Accepts multipart/form-data upload of dataset and query instructions.
    Calculates statistical insights, recommended visualizations, indexes into ChromaDB,
    prompts Gemini LLM, compiles single-page HTML report layout and returns payload to backend.
    """
    # Read the dataset uploaded binary data
    file_bytes = await file.read()
    
    # Run the report service builder pipeline
    report_data = await ReportService.generate_report(
        filename=file.filename,
        file_bytes=file_bytes,
        prompt=prompt
    )
    
    # Format and return the validated response model
    return ReportResponse(
        report_title=report_data["report_title"],
        summary=report_data["summary"],
        content=report_data["content"],
        statistics=report_data["statistics"],
        charts=report_data["charts"]
    )