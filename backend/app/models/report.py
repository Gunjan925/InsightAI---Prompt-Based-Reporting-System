from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text # Imports SQLAlchemy column types and constraints.
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship # Imports relationship() used to create ORM relationships between models.
from datetime import datetime
from app.config.database import Base

# Creates an ORM model named Report. By inheriting from Base, SQLAlchemy knows this class represents a database table.
class Report(Base):
    __tablename__ = "reports" # Specifies the database table name.

    id = Column(Integer, primary_key=True, index=True) # storing each report identifier uniquely
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) # the user to which the particular report belongs to
    file_id = Column(Integer, ForeignKey("uploaded_files.id", ondelete="CASCADE"), nullable=False) # the file of the user for which the report is generated
    prompt = Column(Text, nullable=False) # questions that are added by the user
    report_title = Column(String(255), nullable=False) # title of the report
    summary = Column(Text, nullable=True) # entire summary of the generated reprot
    content = Column(LONGTEXT, nullable=False)  # Long text for reports with embedded charts/HTML. Storing the entire report in HTML format to provide it in the downloadable form
    created_at = Column(DateTime, default=datetime.utcnow) # time at which the report is generated

    # Relationships
    owner = relationship("User", back_populates="reports")
    dataset_file = relationship("UploadedFile", back_populates="reports")