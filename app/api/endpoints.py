from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

# Import Agent mới
from app.core.hybrid_agent import app as hybrid_agent
from app import crud, schemas
from app.database import get_db

router = APIRouter()

# --- Schema Input ---
class QueryInput(BaseModel):
    query: str
    session_id: Optional[int] = None 

# --- Schema Output ---
class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = [] # <--- Trường này sẽ chứa danh sách nguồn

# --- Các API Session (Giữ nguyên) ---
@router.post("/session/start")
def start_new_session(db: Session = Depends(get_db)):
    return crud.create_session(db)

@router.get("/sessions")
def read_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_sessions(db, skip=skip, limit=limit)

@router.delete("/session/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    crud.delete_session(db, session_id)
    return {"status": "success"}

@router.get("/history/{session_id}")
def get_history(session_id: int, db: Session = Depends(get_db)):
    return crud.get_chat_history(db, session_id)

# --- Chat API (CẬP NHẬT) ---
@router.post("/chat", response_model=ChatResponse)
async def chat_with_lawyer(input_data: QueryInput, db: Session = Depends(get_db)):
    if not input_data.query:
        raise HTTPException(status_code=400, detail="Vui lòng nhập câu hỏi")

    # 1. Lấy lịch sử chat (5 tin gần nhất)
    chat_history_text = ""
    if input_data.session_id:
        history = crud.get_chat_history(db, input_data.session_id)
        chat_history_text = "\n".join([f"{msg.sender}: {msg.message}" for msg in history[-5:]])

    # 2. Gọi AGENT
    try:
        inputs = {
            "query": input_data.query,
            "chat_history": chat_history_text
        }
        
        output = hybrid_agent.invoke(inputs)
        
        # Lấy câu trả lời
        final_answer = output.get("generation", "Xin lỗi, hệ thống gặp sự cố.")
        
        # --- LẤY DANH SÁCH NGUỒN ---
        final_sources = output.get("sources", []) # Lấy list nguồn từ state
        
    except Exception as e:
        print(f"❌ Lỗi Agent: {e}")
        final_answer = "Hệ thống đang bảo trì."
        final_sources = []

    # 3. Lưu DB (Lưu ý: DB hiện tại chỉ lưu text, không lưu sources vào lịch sử lâu dài trừ khi sửa DB)
    if input_data.session_id:
        try:
            crud.create_message(db, schemas.MessageCreate(
                session_id=input_data.session_id, sender="user", message=input_data.query
            ))
            crud.create_message(db, schemas.MessageCreate(
                session_id=input_data.session_id, sender="assistant", message=final_answer
            ))
        except Exception as e:
            print(f"[LỖI DB] {e}")

    # 4. Trả về kết quả kèm nguồn
    return ChatResponse(
        answer=final_answer,
        sources=final_sources # <--- Gửi danh sách này cho Frontend
    )