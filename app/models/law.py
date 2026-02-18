from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class SavedLaw(Base):
    __tablename__ = "saved_laws"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    law_id = Column(String(255))  # ID của luật từ qdrant hoặc json
    slug = Column(String(100), nullable=True, unique=True, index=True)  # URL-friendly slug
    law_title = Column(String(500))
    law_type = Column(String(255), nullable=True)  # Loại văn bản: Luật, Nghị định, etc.
    law_year = Column(String(50), nullable=True)
    law_authority = Column(String(255), nullable=True)
    law_content = Column(Text, nullable=True)  # Lưu full content để reference nhanh
    notes = Column(Text, nullable=True)  # Ghi chú của user

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="saved_laws")


class SavedQuestion(Base):
    __tablename__ = "saved_questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text)
    answer = Column(Text, nullable=True)
    law_id = Column(String(255), nullable=True)  # Nếu câu hỏi liên quan đến một luật cụ thể
    tags = Column(JSON, nullable=True)  # Gắn tag để dễ tìm (ví dụ: ["tài chính", "luật thuế"])
    is_bookmarked = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="saved_questions")
