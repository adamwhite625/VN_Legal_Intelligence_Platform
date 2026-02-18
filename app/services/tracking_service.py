"""
User Tracking Service
Xử lý việc lưu luật, lưu câu hỏi, v.v.
"""

from sqlalchemy.orm import Session
from app import models, schemas
from app.utils.slug_generator import create_law_slug
from typing import List, Optional


class TrackingService:
    """Service xử lý user tracking"""

    @staticmethod
    def save_law(
        db: Session,
        user_id: int,
        law_id: str,
        law_title: str,
        law_type: Optional[str] = None,
        law_year: Optional[str] = None,
        law_authority: Optional[str] = None,
        law_content: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> models.SavedLaw:
        """Lưu một luật"""
        
        # Kiểm tra xem đã lưu chưa
        existing = db.query(models.SavedLaw).filter(
            models.SavedLaw.user_id == user_id,
            models.SavedLaw.law_id == law_id
        ).first()
        
        if existing:
            return existing
        
        # Generate slug for the law
        slug = create_law_slug(law_id, law_title)
        
        saved_law = models.SavedLaw(
            user_id=user_id,
            law_id=law_id,
            law_title=law_title,
            law_type=law_type,
            law_year=law_year,
            law_authority=law_authority,
            law_content=law_content,
            notes=notes,
            slug=slug,
        )
        db.add(saved_law)
        db.commit()
        db.refresh(saved_law)
        return saved_law

    @staticmethod
    def unsave_law(db: Session, user_id: int, law_id: str) -> bool:
        """Xóa một luật đã lưu"""
        saved_law = db.query(models.SavedLaw).filter(
            models.SavedLaw.user_id == user_id,
            models.SavedLaw.law_id == law_id
        ).first()
        
        if saved_law:
            db.delete(saved_law)
            db.commit()
            return True
        return False

    @staticmethod
    def get_saved_laws(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.SavedLaw]:
        """Lấy danh sách luật đã lưu"""
        return db.query(models.SavedLaw).filter(
            models.SavedLaw.user_id == user_id
        ).order_by(models.SavedLaw.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def is_law_saved(db: Session, user_id: int, law_id: str) -> bool:
        """Kiểm tra xem luật đã được lưu chưa"""
        saved = db.query(models.SavedLaw).filter(
            models.SavedLaw.user_id == user_id,
            models.SavedLaw.law_id == law_id
        ).first()
        return saved is not None

    @staticmethod
    def save_question(
        db: Session,
        user_id: int,
        question: str,
        answer: Optional[str] = None,
        law_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> models.SavedQuestion:
        """Lưu một câu hỏi"""
        saved_question = models.SavedQuestion(
            user_id=user_id,
            question=question,
            answer=answer,
            law_id=law_id,
            tags=tags or [],
        )
        db.add(saved_question)
        db.commit()
        db.refresh(saved_question)
        return saved_question

    @staticmethod
    def update_question_answer(
        db: Session,
        question_id: int,
        user_id: int,
        answer: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_bookmarked: Optional[bool] = None,
    ) -> Optional[models.SavedQuestion]:
        """Cập nhật câu hỏi đã lưu"""
        question = db.query(models.SavedQuestion).filter(
            models.SavedQuestion.id == question_id,
            models.SavedQuestion.user_id == user_id
        ).first()
        
        if not question:
            return None
        
        if answer is not None:
            question.answer = answer
        if tags is not None:
            question.tags = tags
        if is_bookmarked is not None:
            question.is_bookmarked = is_bookmarked
        
        db.commit()
        db.refresh(question)
        return question

    @staticmethod
    def delete_question(db: Session, question_id: int, user_id: int) -> bool:
        """Xóa câu hỏi đã lưu"""
        question = db.query(models.SavedQuestion).filter(
            models.SavedQuestion.id == question_id,
            models.SavedQuestion.user_id == user_id
        ).first()
        
        if question:
            db.delete(question)
            db.commit()
            return True
        return False

    @staticmethod
    def get_saved_questions(
        db: Session,
        user_id: int,
        law_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.SavedQuestion]:
        """Lấy danh sách câu hỏi đã lưu"""
        query = db.query(models.SavedQuestion).filter(
            models.SavedQuestion.user_id == user_id
        )
        
        if law_id:
            query = query.filter(models.SavedQuestion.law_id == law_id)
        
        return query.order_by(models.SavedQuestion.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_questions_for_law(db: Session, user_id: int, law_id: str) -> List[models.SavedQuestion]:
        """Lấy tất cả câu hỏi của user cho một luật cụ thể"""
        return db.query(models.SavedQuestion).filter(
            models.SavedQuestion.user_id == user_id,
            models.SavedQuestion.law_id == law_id
        ).order_by(models.SavedQuestion.created_at.desc()).all()

    @staticmethod
    def get_sessions_for_law(db: Session, user_id: int, law_id: str) -> List[models.ChatSession]:
        """Lấy tất cả session của user cho một luật"""
        return db.query(models.ChatSession).filter(
            models.ChatSession.user_id == user_id,
            models.ChatSession.session_type == "law-detail",
            models.ChatSession.law_id == law_id
        ).order_by(models.ChatSession.created_at.desc()).all()

    @staticmethod
    def get_tracking_stats(db: Session, user_id: int) -> dict:
        """Lấy thống kê tracking của user"""
        saved_laws_count = db.query(models.SavedLaw).filter(
            models.SavedLaw.user_id == user_id
        ).count()
        
        saved_questions_count = db.query(models.SavedQuestion).filter(
            models.SavedQuestion.user_id == user_id
        ).count()
        
        sessions_count = db.query(models.ChatSession).filter(
            models.ChatSession.user_id == user_id
        ).count()
        
        recent_sessions = db.query(models.ChatSession).filter(
            models.ChatSession.user_id == user_id
        ).order_by(models.ChatSession.created_at.desc()).limit(5).all()
        
        return {
            "total_saved_laws": saved_laws_count,
            "total_saved_questions": saved_questions_count,
            "total_sessions": sessions_count,
            "recent_sessions": [
                {
                    "id": s.id,
                    "session_type": s.session_type,
                    "law_id": s.law_id,
                    "title": s.title,
                    "created_at": s.created_at,
                }
                for s in recent_sessions
            ]
        }
