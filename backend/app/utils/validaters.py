# checking the correct validations by using the constants from the constants.py file

import os
from fastapi import HTTPException, status
from app.utils.constants import ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, MAX_FILE_SIZE_BYTES

def validate_uploaded_file(filename: str, size: int, content_type: str):
    """
    Validates the uploaded file's extension, size, and MIME type.
    Raises HTTPException if validation fails.
    """
    # 1. Validate file extension
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Only CSV and Excel (.xlsx, .xls) files are allowed."
        )
    
    # 2. Validate file size
    if size > MAX_FILE_SIZE_BYTES:
        max_size_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File is too large. Maximum allowed size is {max_size_mb:.1f} MB."
        )

    # 3. Validate MIME type
    # We validate but allow minor variations since browsers send different MIME types for Excel
    if content_type not in ALLOWED_MIME_TYPES and not filename.lower().endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported media type '{content_type}'."
        )