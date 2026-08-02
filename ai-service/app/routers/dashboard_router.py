# API endpoints for generating the initial dashboard after a dataset is uploaded.
from fastapi import APIRouter, Depends, UploadFile, File, status
from app.services.dashboard_service import DashboardService
from app.schemas.response_schema import DashboardResponse

# Create the router for dashboard calculations
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.post("", response_model=DashboardResponse, status_code=status.HTTP_200_OK)
async def generate_dashboard(file: UploadFile = File(...)) -> DashboardResponse:
    """
    Receives an uploaded CSV or Excel dataset binary, cleans it, calculates descriptive metrics,
    and returns suggested chart configurations without utilizing an LLM.
    Useful for generating immediate interactive visualizations on dataset upload.
    """
    # Read the file upload bytes
    file_bytes = await file.read()
    
    # Process the file via dashboard service pipeline
    result = DashboardService.process_dataset(file.filename, file_bytes)
    
    # Format and return the validated response model
    return DashboardResponse(
        dataset_id=result["dataset_id"],
        row_count=result["row_count"],
        col_count=result["col_count"],
        columns=result["columns"],
        charts=result["charts"]
    )