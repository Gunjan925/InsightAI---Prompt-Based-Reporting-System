from pydantic import BaseModel
from datetime import datetime

# If the input is an object, read its attributes (user.id, user.username, etc.) instead of expecting a dictionary.
class UploadResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    mime_type: str
    created_at: datetime

    class Config:
        from_attributes = True