from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base

# Creates an ORM model named User. By inheriting from Base, SQLAlchemy knows this class represents a database table.
class User(Base):
    __tablename__ = "users"  # Specifies the database table name.

    id = Column(Integer, primary_key=True, index=True) # storing each user identifier uniquely
    username = Column(String(50), unique=True, index=True, nullable=False) # the unique username created by the user
    email = Column(String(100), unique=True, index=True, nullable=False) # email of the user
    hashed_password = Column(String(255), nullable=False) # hashed password of the user stored
    created_at = Column(DateTime, default=datetime.utcnow) # time at which the user is created

    # Relationships to user's uploaded files and reports
    files = relationship("UploadedFile", back_populates="owner", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="owner", cascade="all, delete-orphan")