from sqlalchemy.orm import Session
from app.schemas.upload_schema import UploadResponse
from app.services.upload_service import UploadService

class UploadController:
    @staticmethod
    def upload_file(
        db: Session,
        filename: str,
        content_type: str,
        file_content: bytes, # Receives the uploaded file's binary content (bytes).
        user_id: int
    ) -> UploadResponse:
        """
        Processes the uploaded file and returns metadata response.
        """
        uploaded_file = UploadService.process_and_store_file(
            db=db,
            filename=filename,
            content_type=content_type,
            file_content=file_content,
            user_id=user_id
        )
        return UploadResponse.from_orm(uploaded_file)