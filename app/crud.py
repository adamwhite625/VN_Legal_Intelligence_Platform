from sqlalchemy.orm import Session
from sqlalchemy import desc
from app import models, schemas

# 1. Tạo phiên chat mới
def create_session(db: Session):
    db_session = models.ChatSession()
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

# 2. Lấy danh sách các phiên chat (kèm tin nhắn đầu tiên để làm preview)
def get_sessions(db: Session, skip: int = 0, limit: int = 100):
    # Lấy session sắp xếp theo thời gian mới nhất
    sessions = db.query(models.ChatSession).order_by(desc(models.ChatSession.created_at)).offset(skip).limit(limit).all()
    
    results = []
    for session in sessions:
        # Lấy tin nhắn đầu tiên của user để làm title hiển thị
        first_msg = db.query(models.ChatMessage).filter(
            models.ChatMessage.session_id == session.id,
            models.ChatMessage.sender == 'user'
        ).order_by(models.ChatMessage.sent_at.asc()).first()
        
        preview = first_msg.message if first_msg else "Phiên chat mới"
        if len(preview) > 50:
            preview = preview[:50] + "..."
            
        results.append({
            "id": session.id,
            "created_at": session.created_at,
            "first_message": preview
        })
    return results

# 3. Lưu tin nhắn
def create_message(db: Session, message: schemas.MessageCreate):
    db_message = models.ChatMessage(
        session_id=message.session_id,
        sender=message.sender,
        message=message.message
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

# 4. Lấy lịch sử tin nhắn của 1 session
def get_chat_history(db: Session, session_id: int):
    return db.query(models.ChatMessage).filter(
        models.ChatMessage.session_id == session_id
    ).order_by(models.ChatMessage.sent_at.asc()).all()

# 5. Xóa session
def delete_session(db: Session, session_id: int):
    db_session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False