from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import schemas, models
from app.api.v1 import deps
from app.services.context_chat_service import ContextAwareChatService
from app.core.limiter import limiter

router = APIRouter()

@router.post("/send", response_model=schemas.ChatResponse)
@limiter.limit("5/minute")
async def chat_with_lawyer(
    request: Request,
    input_data: schemas.QueryInput,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Chat endpoint với context awareness
    
    context_type: "general" (consultant) hoặc "law-detail"
    law_id: Cần khi context_type="law-detail"
    """
    return await ContextAwareChatService.process_context_chat(
        db=db,
        current_user=current_user,
        input_data=input_data,
    )

@router.get("/sessions")
def read_sessions(
    skip: int = 0, limit: int = 100, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Lấy danh sách session của user hiện tại"""
    return db.query(models.ChatSession).filter(
        models.ChatSession.user_id == current_user.id
    ).order_by(models.ChatSession.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/history/{session_id}", response_model=schemas.SessionHistory)
def get_history(
    session_id: int, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Lấy lịch sử của một session"""
    return ContextAwareChatService.get_session_history(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
    )

@router.get("/summaries/{session_id}", response_model=List[schemas.MessageSummaryResponse])
def get_summaries(
    session_id: int, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Lấy danh sách summary cho một session"""
    return ContextAwareChatService.get_summaries_for_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
    )

@router.post("/session/start")
def start_session(
    session_type: str = "general",
    law_id: str = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Tạo một session mới"""
    new_session = models.ChatSession(
        user_id=current_user.id,
        session_type=session_type,
        law_id=law_id if session_type == "law-detail" else None,
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.delete("/session/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Xóa một session"""
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id,
        models.ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
    return {"message": "Session deleted"}
