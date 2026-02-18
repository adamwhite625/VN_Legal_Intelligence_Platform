from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class ChatSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_type = Column(String(50), default="general")  # "general" hoặc "law-detail"
    law_id = Column(String(255), nullable=True)  # Nếu session_type="law-detail"
    title = Column(String(500), nullable=True)  # Tiêu đề session
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    summaries = relationship("MessageSummary", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    sender = Column(String(50))  # user hoặc assistant

    # Dùng Text thay vì String để lưu tin nhắn dài không giới hạn
    message = Column(Text)
    sources = Column(JSON, nullable=True)  # Lưu sources (từ qdrant hoặc khác)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")


class MessageSummary(Base):
    __tablename__ = "message_summaries"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    summary = Column(Text)
    message_count = Column(Integer)  # Số lượng message được summarize (thường là 5)
    summarized_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="summaries")
