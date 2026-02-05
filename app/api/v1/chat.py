from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models
from app.api import deps
# Import Graph AI từ Service Layer (Bạn cần di chuyển folder agents trước)
from app.services.law_agent.graph import app as agent_app 
from app.services.formatters import format_sources 

router = APIRouter()

@router.post("/send", response_model=schemas.ChatResponse)
async def chat_with_lawyer(
    input_data: schemas.QueryInput,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    if not input_data.query:
        raise HTTPException(status_code=400, detail="Query empty")

    # 1. Xử lý Session & Lịch sử
    chat_history_text = ""
    if input_data.session_id:
        session = db.query(models.ChatSession).filter(
            models.ChatSession.id == input_data.session_id,
            models.ChatSession.user_id == current_user.id
        ).first()
        
        # Nếu session không tồn tại hoặc không phải của user -> Tạo mới
        if not session:
            new_session = models.ChatSession(user_id=current_user.id)
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            input_data.session_id = new_session.id
        else:
            # Lấy 5 tin nhắn gần nhất
            history = db.query(models.Message).filter(
                models.Message.session_id == input_data.session_id
            ).order_by(models.Message.created_at.asc()).all()
            chat_history_text = "\n".join([f"{msg.sender}: {msg.message}" for msg in history[-5:]])

    # 2. Gọi AI Service
    try:
        inputs = {"query": input_data.query, "chat_history": chat_history_text}
        output = agent_app.invoke(inputs)
        final_answer = output.get("generation", "Lỗi xử lý")
        raw_sources = output.get("sources", [])
        
        # Format sources để hiển thị đẹp
        if raw_sources:
            formatted_list, _ = format_sources(
                [{"source": src, "content": ""} for src in raw_sources]
            )
            final_sources = formatted_list
        else:
            final_sources = []
    except Exception as e:
        print(f"Agent Error: {e}")
        final_answer = "Hệ thống đang bảo trì."
        final_sources = []

    # 3. Lưu tin nhắn vào DB
    if input_data.session_id:
        user_msg = models.Message(session_id=input_data.session_id, sender="user", message=input_data.query)
        bot_msg = models.Message(session_id=input_data.session_id, sender="assistant", message=final_answer)
        db.add_all([user_msg, bot_msg])
        db.commit()

    return schemas.ChatResponse(answer=final_answer, sources=final_sources)

@router.get("/sessions")
def read_sessions(
    skip: int = 0, limit: int = 100, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    # Lấy danh sách session của user hiện tại
    return db.query(models.ChatSession).filter(
        models.ChatSession.user_id == current_user.id
    ).order_by(models.ChatSession.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/history/{session_id}")
def get_history(
    session_id: int, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    # Kiểm tra quyền
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id,
        models.ChatSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=403, detail="Access denied")
        
    return db.query(models.Message).filter(
        models.Message.session_id == session_id
    ).order_by(models.Message.created_at.asc()).all()

@router.post("/session/start")
def start_session(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    new_session = models.ChatSession(user_id=current_user.id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session