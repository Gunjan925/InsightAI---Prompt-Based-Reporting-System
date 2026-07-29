from sqlalchemy.orm import Session
from typing import List
from app.schemas.report_schema import ReportListItem, DashboardStats
from app.services.history_service import HistoryService

class HistoryController:
    @staticmethod
    def get_history(db: Session, user_id: int) -> List[ReportListItem]:
        """
        Retrieves user report history.
        """
        history_data = HistoryService.get_user_report_history(db, user_id)
        # Parse into response schemas
        return [ReportListItem(**item) for item in history_data]

    @staticmethod
    def get_dashboard_stats(db: Session, user_id: int) -> DashboardStats:
        """
        Retrieves user dashboard statistics.
        """
        stats_data = HistoryService.get_dashboard_stats(db, user_id)
        return DashboardStats(**stats_data)

'''
** is the dictionary unpacking operator.
Instead of writing
ReportListItem(
    id=item["id"],
    title=item["title"],
    created_at=item["created_at"]
)
you simply write : ReportListItem(**item)
Python automatically converts
{
    "id": 1,
    "title": "Sales Report",
    "created_at": "2026-07-25"
}
into
ReportListItem(
    id=1,
    title="Sales Report",
    created_at="2026-07-25"
)
'''