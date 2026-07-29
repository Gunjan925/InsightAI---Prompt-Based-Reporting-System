from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.report_schema import DashboardStats
from app.controllers.history_controller import HistoryController
from app.middlewares.auth import get_current_user
from app.models.user import User

# Creates a group of related API endpoints. Adds /dashboard before every endpoint (/dashboard/stats). Groups these APIs under Dashboard in Swagger UI.
# Swagger UI is an automatically generated interactive webpage that documents all your FastAPI APIs. It lets you view, test, and understand your endpoints without using tools like Postman. Swagger UI: http://127.0.0.1:8000/docs — Interactive documentation where you can test APIs.
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Depends(get_current_user) : Ensures the request contains a valid JWT token and returns the logged-in user.
@router.get("/stats", response_model=DashboardStats, status_code=status.HTTP_200_OK)
def get_dashboard_stats(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    """
    Get dashboard metrics (total files, total reports, latest activities, file format distributions).
    """
    return HistoryController.get_dashboard_stats(db, current_user.id)