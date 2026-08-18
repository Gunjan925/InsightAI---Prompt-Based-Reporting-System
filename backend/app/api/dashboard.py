from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.config.database import get_db
from app.schemas.report_schema import DashboardStats
from app.controllers.history_controller import HistoryController
from app.middlewares.auth import get_current_user
from app.models.user import User
from app.models.uploaded_file import UploadedFile
from app.services.ai_client import AiClient
from fastapi import HTTPException

# Creates a group of related API endpoints. Adds /dashboard before every endpoint (/dashboard/stats). Groups these APIs under Dashboard in Swagger UI.
# Swagger UI is an automatically generated interactive webpage that documents all your FastAPI APIs. It lets you view, test, and understand your endpoints without using tools like Postman. Swagger UI: http://127.0.0.1:8000/docs — Interactive documentation where you can test APIs.
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Depends(get_current_user) : Ensures the request contains a valid JWT token and returns the logged-in user.
@router.get("/stats", response_model=DashboardStats, status_code=status.HTTP_200_OK)
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get dashboard metrics (total files, total reports, latest activities, file format distributions).
    """
    return HistoryController.get_dashboard_stats(db, current_user.id)


# Request body schema for the dataset dashboard generation endpoint
class DashboardGenerateRequest(BaseModel):
    file_id: int


@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_dataset_dashboard(
    request: DashboardGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Phase 1 of the two-phase workflow.
    Accepts a file_id, retrieves the dataset binary from MySQL, and forwards it to the AI Service's /api/dashboard endpoint for instant chart generation WITHOUT any LLM.
    Returns: { dataset_id, row_count, col_count, columns, charts[] }
    Each chart contains type, title, description, and plotly_json (a serialised Plotly figure).
    """
    # Fetch the uploaded file from MySQL and verify ownership
    db_file = db.query(UploadedFile).filter(
        UploadedFile.id == request.file_id,
        UploadedFile.user_id == current_user.id
    ).first()

    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset file not found or access denied."
        )

    # Forward the file binary to the AI Service for non-LLM dashboard generation
    dashboard_data = await AiClient.generate_dashboard_from_ai_service(
        filename=db_file.filename,
        file_content=db_file.file_content,
        mime_type=db_file.mime_type
    )

    return dashboard_data


@router.get("/generate/{file_id}", status_code=status.HTTP_200_OK)
async def get_dataset_dashboard(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the dataset file from MySQL by file_id (confirming ownership),
    forwards it to the AI Service for cleaning, statistics, and Plotly chart generation (non-LLM),
    and returns: { dataset_id, row_count, col_count, columns, charts[] }
    """
    # Fetch file record from MySQL and verify user ownership
    db_file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        UploadedFile.user_id == current_user.id
    ).first()

    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset file not found or access denied."
        )

    # Call the AI Service's non-LLM dashboard endpoint
    dashboard_data = await AiClient.generate_dashboard_from_ai_service(
        filename=db_file.filename,
        file_content=db_file.file_content,
        mime_type=db_file.mime_type
    )

    return dashboard_data