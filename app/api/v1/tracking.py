"""
Tracking API Router
Xử lý:
- Save/Unsave laws
- Save/Delete questions
- Get tracking stats
- Get questions for a law
- Get sessions for a law
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.api.v1 import deps
from app.services.tracking_service import TrackingService
from app.schemas.tracking import (
    SavedLawCreate, SavedLawResponse,
    SavedQuestionCreate, SavedQuestionUpdate, SavedQuestionResponse,
    UserTrackingStats
)

router = APIRouter()


@router.post("/laws/save", response_model=SavedLawResponse)
def save_law(
    data: SavedLawCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Lưu một luật"""
    saved_law = TrackingService.save_law(
        db=db,
        user_id=current_user.id,
        law_id=data.law_id,
        law_title=data.law_title,
        law_type=data.law_type,
        law_year=data.law_year,
        law_authority=data.law_authority,
        law_content=data.law_content,
        notes=data.notes,
    )
    return saved_law


@router.delete("/laws/{law_id}/unsave")
def unsave_law(
    law_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Xóa một luật đã lưu"""
    success = TrackingService.unsave_law(db=db, user_id=current_user.id, law_id=law_id)
    if not success:
        raise HTTPException(status_code=404, detail="Saved law not found")
    return {"message": "Law removed from saved"}


@router.get("/laws/is-saved/{law_id}")
def check_law_saved(
    law_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Kiểm tra xem luật đã được lưu chưa"""
    is_saved = TrackingService.is_law_saved(db=db, user_id=current_user.id, law_id=law_id)
    return {"is_saved": is_saved}


@router.get("/laws", response_model=List[SavedLawResponse])
def get_saved_laws(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Lấy danh sách luật đã lưu"""
    laws = TrackingService.get_saved_laws(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return laws


@router.post("/questions", response_model=SavedQuestionResponse)
def save_question(
    data: SavedQuestionCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Lưu một câu hỏi"""
    question = TrackingService.save_question(
        db=db,
        user_id=current_user.id,
        question=data.question,
        answer=data.answer,
        law_id=data.law_id,
        tags=data.tags,
    )
    return question


@router.put("/questions/{question_id}", response_model=SavedQuestionResponse)
def update_question(
    question_id: int,
    data: SavedQuestionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Cập nhật câu hỏi đã lưu"""
    question = TrackingService.update_question_answer(
        db=db,
        question_id=question_id,
        user_id=current_user.id,
        answer=data.answer,
        tags=data.tags,
        is_bookmarked=data.is_bookmarked,
    )
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question


@router.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Xóa câu hỏi đã lưu"""
    success = TrackingService.delete_question(
        db=db,
        question_id=question_id,
        user_id=current_user.id,
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return {"message": "Question deleted"}


@router.get("/questions", response_model=List[SavedQuestionResponse])
def get_saved_questions(
    law_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Lấy danh sách câu hỏi đã lưu"""
    questions = TrackingService.get_saved_questions(
        db=db,
        user_id=current_user.id,
        law_id=law_id,
        skip=skip,
        limit=limit,
    )
    return questions


@router.get("/laws/{law_id}/questions", response_model=List[SavedQuestionResponse])
def get_questions_for_law(
    law_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Lấy tất cả câu hỏi của user cho một luật"""
    questions = TrackingService.get_questions_for_law(
        db=db,
        user_id=current_user.id,
        law_id=law_id,
    )
    return questions


@router.get("/laws/{law_id}/sessions")
def get_sessions_for_law(
    law_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Lấy tất cả session của user cho một luật"""
    sessions = TrackingService.get_sessions_for_law(
        db=db,
        user_id=current_user.id,
        law_id=law_id,
    )
    return [
        {
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }
        for s in sessions
    ]


@router.get("/stats", response_model=UserTrackingStats)
def get_tracking_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """Lấy thống kê tracking của user"""
    stats = TrackingService.get_tracking_stats(db=db, user_id=current_user.id)
    return stats
