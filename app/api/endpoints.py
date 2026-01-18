from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

# Import logic AI
from app.core.gemini_client import get_law_answer

# Import Database
from app import crud, schemas
from app.database import get_db

router = APIRouter()

# --- Schema Input ---
class QueryInput(BaseModel):
    query: str
    session_id: Optional[int] = None 

class ChatResponse(BaseModel):
    answer: str
    sources: list = []

# --- Session APIs (Giữ nguyên) ---
@router.post("/session/start")
def start_new_session(db: Session = Depends(get_db)):
    return crud.create_session(db)

@router.get("/sessions")
def read_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_sessions(db, skip=skip, limit=limit)

@router.delete("/session/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    success = crud.delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success", "message": "Session deleted"}

@router.get("/history/{session_id}")
def get_history(session_id: int, db: Session = Depends(get_db)):
    return crud.get_chat_history(db, session_id)

# --- Chat API ---
@router.post("/chat", response_model=ChatResponse)
async def chat_with_lawyer(input_data: QueryInput, db: Session = Depends(get_db)):
    if not input_data.query:
        raise HTTPException(status_code=400, detail="Vui lòng nhập câu hỏi")

    # 1. Gọi AI lấy câu trả lời
    result = get_law_answer(input_data.query)

    # 2. Lưu vào Database (SỬA ĐOẠN NÀY ĐỂ KHỚP CRUD)
    if input_data.session_id:
        try:
            # Lưu câu hỏi của User
            crud.create_message(db, schemas.MessageCreate(
                session_id=input_data.session_id,
                sender="user",           # <--- Khớp với crud.py
                message=input_data.query # <--- Khớp với crud.py
            ))
            
            # Lưu câu trả lời của AI
            crud.create_message(db, schemas.MessageCreate(
                session_id=input_data.session_id,
                sender="assistant",      # <--- Khớp với crud.py
                message=result["answer"] # <--- Khớp với crud.py
            ))
            print(f"[THÀNH CÔNG] Đã lưu tin nhắn vào Session {input_data.session_id}")
        except Exception as e:
            # In lỗi chi tiết ra để debug
            print(f"[LỖI DATABASE] {e}")

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"]
    )