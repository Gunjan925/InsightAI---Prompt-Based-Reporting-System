# Health-check endpoint used by the backend to verify the AI service is available.
from fastapi import APIRouter, status
from app.schemas.response_schema import HealthResponse

# Register a health check router
router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def check_health() -> HealthResponse:
    """
    Standard health check endpoint used by the primary backend to check if the AI Service is online.
    """
    return HealthResponse(status="ok", version="1.0.0")