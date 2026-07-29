import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.uploaded_file import UploadedFile
from app.models.report import Report
from app.services.ai_client import AiClient

logger = logging.getLogger("app")

class ReportService:
    @staticmethod
    async def generate_and_save_report(
        db: Session,
        file_id: int,
        prompt: str,
        user_id: int
    ) -> Report:
        """
        Retrieves the dataset file from DB, validates ownership, sends details to AI service,
        saves the resulting report in MySQL, and returns the DB model.
        """
        # Fetch file and verify user ownership
        db_file = db.query(UploadedFile).filter(
            UploadedFile.id == file_id,
            UploadedFile.user_id == user_id
        ).first()

        '''
        Equivalent sql query : 
        SELECT *
        FROM uploaded_files
        WHERE id = ?
        AND user_id = ?
        LIMIT 1;
        '''
        
        if not db_file:
            logger.warning(f"Report generation request rejected: File ID {file_id} not found or unauthorized for user {user_id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset file not found or unauthorized access"
            )

        logger.info(f"Initiating report generation for File ID {file_id} by User ID {user_id}.")
        
        # Call the external AI service
        ai_response = await AiClient.generate_report_from_ai_service(
            filename=db_file.filename,
            file_content=db_file.file_content,
            mime_type=db_file.mime_type,
            prompt=prompt
        )
        
        # Save generated report details to MySQL database
        new_report = Report(
            user_id=user_id,
            file_id=file_id,
            prompt=prompt,
            report_title=ai_response["report_title"],
            summary=ai_response["summary"],
            content=ai_response["content"]
        )
        
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        
        logger.info(f"Report ID {new_report.id} ('{new_report.report_title}') generated and saved to DB for user {user_id}.")
        return new_report

    @staticmethod
    def get_report_by_id(db: Session, report_id: int, user_id: int) -> Report:
        """
        Retrieves a report by its ID, verifying user ownership.
        """
        db_report = db.query(Report).filter(
            Report.id == report_id,
            Report.user_id == user_id
        ).first()
        
        if not db_report:
            logger.warning(f"Access denied: Report ID {report_id} not found or unauthorized for user {user_id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found or unauthorized access"
            )
            
        return db_report