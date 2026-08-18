from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.schemas.upload_schema import UploadResponse
from app.controllers.upload_controller import UploadController
from app.middlewares.auth import get_current_user
from app.models.user import User
from app.models.uploaded_file import UploadedFile

# Creates a group of related API endpoints. Adds /upload before every endpoint (/upload). Groups these APIs under Dataset Upload in Swagger UI.
# Swagger UI is an automatically generated interactive webpage that documents all your FastAPI APIs. It lets you view, test, and understand your endpoints without using tools like Postman. Swagger UI: http://127.0.0.1:8000/docs — Interactive documentation where you can test APIs.
router = APIRouter(prefix="/upload", tags=["Dataset Upload"])

# file → Parameter that receives the uploaded file.
# UploadFile → FastAPI class representing an uploaded file.
# File(...) → Marks this parameter as required and tells FastAPI to expect it in multipart/form-data.
# multipart/form-data is an HTTP request format used when a client sends files (or files along with normal form fields) to a server.
@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(file: UploadFile = File(...),db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    """
    Upload a structured dataset (CSV or Excel) to the reporting platform.
    Validates file format, MIME type, and size constraints, storing binary content in the DB.
    """
    file_content = await file.read()
    return UploadController.upload_file(
        db=db,
        filename=file.filename,
        content_type=file.content_type,
        file_content=file_content,
        user_id=current_user.id
    )

# complete workflow of above function
'''
Client uploads CSV

        │
        ▼

FastAPI receives file

        │
        ▼

JWT verified

        │
        ▼

Database session created

        │
        ▼

File read into bytes

        │
        ▼

UploadController.upload_file()

        │
        ▼

Validate file

        │
        ▼

Store in Database

        │
        ▼

Return UploadResponse
'''

@router.get("", response_model=List[UploadResponse], status_code=status.HTTP_200_OK)
def get_user_datasets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve a list of all datasets previously uploaded by the authenticated user.
    """
    files = db.query(UploadedFile).filter(UploadedFile.user_id == current_user.id).order_by(UploadedFile.created_at.desc()).all()
    return files


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(file_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Permanently delete an uploaded dataset by its ID.
    Only the user who uploaded the file can delete it.
    """
    record = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found.")
    if record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this dataset.")
    db.delete(record)
    db.commit()
    return