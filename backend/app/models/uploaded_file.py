from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base

# Creates an ORM model named UploadedFile. By inheriting from Base, SQLAlchemy knows this class represents a database table.
class UploadedFile(Base):
    __tablename__ = "uploaded_files" # Specifies the database table name.

    id = Column(Integer, primary_key=True, index=True) # storing each uploaded file identifier uniquely
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) # the user who uploaded the file
    filename = Column(String(255), nullable=False) # name of the file which is uploaded by the user
    file_content = Column(LargeBinary(length=16777215), nullable=False)  # MEDIUMBLOB, up to 16MB . Actual content of the file
    file_size = Column(Integer, nullable=False)  # In bytes
    mime_type = Column(String(100), nullable=False) # file format like csv or excel
    created_at = Column(DateTime, default=datetime.utcnow) # time at which file was uploaded

    # Relationships
    owner = relationship("User", back_populates="files") # The User model has a relationship attribute named files.
    reports = relationship("Report", back_populates="dataset_file", cascade="all, delete-orphan")

'''
Think of back_populates as a two-way link
User
 ├── files  ----------------------► UploadedFile
 │                                     ▲
 │                                     │
 └──────────── back_populates ◄────────┘
                  owner
UploadedFile
 ├── reports --------------------► Report
 │                                   ▲
 │                                   │
 └────────── back_populates ◄────────┘
              dataset_file
'''