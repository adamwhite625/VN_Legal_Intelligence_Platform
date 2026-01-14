from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Quan hệ 1-nhiều với tin nhắn
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    sender = Column(String(50))  # "user" hoặc "bot"
    message = Column(Text)       # Nội dung tin nhắn (Dùng Text thay vì NVARCHAR(MAX))
    sent_at = Column(DateTime, default=datetime.now)

    # Quan hệ ngược lại với session
    session = relationship("ChatSession", back_populates="messages")