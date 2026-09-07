from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_id = Column(Integer, ForeignKey("uploaded_files.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False, default="New Discussion")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    owner = relationship("User")
    dataset_file = relationship("UploadedFile")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(50), nullable=False) # 'user' or 'bot'
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    session = relationship("ChatSession", back_populates="messages")
