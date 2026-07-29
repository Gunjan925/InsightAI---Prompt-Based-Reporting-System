import logging
from sqlalchemy.orm import Session
from app.models.uploaded_file import UploadedFile
from app.utils.validaters import validate_uploaded_file

logger = logging.getLogger("app")

# to save the uploaded file
class UploadService:
    @staticmethod
    def process_and_store_file(
        db: Session,
        filename: str,
        content_type: str,
        file_content: bytes,
        user_id: int
    ) -> UploadedFile:
        """
        Validates the uploaded file and stores it directly in the MySQL database as binary data (BLOB).
        Does not write files to local disk storage.
        """
        file_size = len(file_content)
        
        # Perform validation on file name extension, size, and type
        validate_uploaded_file(filename, file_size, content_type)
        
        # Save record in the database
        db_file = UploadedFile(
            user_id=user_id,
            filename=filename,
            file_content=file_content,
            file_size=file_size,
            mime_type=content_type
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        logger.info(f"File '{filename}' (ID: {db_file.id}, Size: {file_size} bytes) stored in DB by user ID {user_id}.")
        return db_file