from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # MySQL bắt buộc String phải có độ dài, ví dụ String(255)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="user")  # user hoặc admin

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sessions = relationship("ChatSession", back_populates="user")
    saved_laws = relationship("SavedLaw", back_populates="user", cascade="all, delete-orphan")
    saved_questions = relationship(
        "SavedQuestion", back_populates="user", cascade="all, delete-orphan"
    )
