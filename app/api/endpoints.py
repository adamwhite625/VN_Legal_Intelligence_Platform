from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

from pydantic import BaseModel
from app.core.search_qdrant import search_relevant_documents
from app.core.utils import format_docs_for_context
from app.core.gemini_client import generate_answer

router = APIRouter()

# --- Thêm Schema Input cho Chat ---
class QueryInput(BaseModel):
    query: str
    session_id: int = None # Tùy chọn, để lưu lịch sử sau này

class ChatResponse(BaseModel):
    answer: str
    sources: list = [] # Trả về danh sách nguồn tham khảo

# --- Session APIs ---

@router.post("/session/start", response_model=schemas.SessionResponse)
def start_new_session(db: Session = Depends(get_db)):
    """Tạo phiên chat mới"""
    return crud.create_session(db)

@router.get("/sessions", response_model=List[schemas.SessionResponse])
def read_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lấy danh sách các phiên chat cũ"""
    return crud.get_sessions(db, skip=skip, limit=limit)

@router.delete("/session/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    """Xóa một phiên chat"""
    success = crud.delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success", "message": "Session deleted"}

# --- Message APIs ---

@router.post("/message/save", response_model=schemas.MessageResponse)
def save_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    """Lưu tin nhắn (User hoặc Bot)"""
    return crud.create_message(db, message)

@router.get("/history/{session_id}", response_model=List[schemas.MessageResponse])
def get_history(session_id: int, db: Session = Depends(get_db)):
    """Lấy toàn bộ lịch sử chat của session"""
    return crud.get_chat_history(db, session_id)

# --- Chat API ---

@router.post("/chat/gemini", response_model=ChatResponse)
async def chat_with_gemini(input_data: QueryInput):
    """
    API Chat chính:
    1. Tìm kiếm Qdrant
    2. Gửi context + query cho Gemini
    3. Trả về kết quả
    """
    # 1. Tìm kiếm documents
    # Lưu ý: Nếu Qdrant chưa có data thì search_results sẽ rỗng
    search_results = search_relevant_documents(input_data.query, top_k=5)
    
    # 2. Xử lý documents thành context string
    context_text = format_docs_for_context(search_results)
    
    # 3. Lấy nguồn tham khảo (metadata) để hiển thị cho user
    sources = []
    for doc in search_results:
        # Lấy metadata an toàn
        meta = doc.payload if doc.payload else {}
        source_info = f"{meta.get('loai_van_ban', '')} {meta.get('so_hieu', '')}"
        if source_info.strip():
            sources.append(source_info)
    
    # 4. Sinh câu trả lời từ Gemini
    answer = generate_answer(input_data.query, context_text)
    
    return {
        "answer": answer,
        "sources": list(set(sources)) # Loại bỏ nguồn trùng lặp
    }