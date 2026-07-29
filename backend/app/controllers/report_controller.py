from sqlalchemy.orm import Session
from app.schemas.report_schema import ReportGenerateRequest, ReportResponse
from app.services.report_service import ReportService

# Controller class that coordinates report-related requests.
class ReportController:
    @staticmethod
    async def generate_report(
        db: Session,
        request: ReportGenerateRequest, # Receives the validated report generation request containing the file ID and prompt.
        user_id: int
    ) -> ReportResponse:
        """
        Triggers AI report generation for the uploaded dataset and returns full report.
        """
        report = await ReportService.generate_and_save_report(
            db=db,
            file_id=request.file_id,
            prompt=request.prompt,
            user_id=user_id
        )
        return ReportResponse.from_orm(report) # converting the report into the ReportResponse classf format

    @staticmethod
    def get_report(db: Session, report_id: int, user_id: int) -> ReportResponse:
        """
        Retrieves a report for the authenticated user by report ID.
        """
        report = ReportService.get_report_by_id(db=db, report_id=report_id, user_id=user_id)
        return ReportResponse.from_orm(report)