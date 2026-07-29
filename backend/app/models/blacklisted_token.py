from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.config.database import Base

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)
