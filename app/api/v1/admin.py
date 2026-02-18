from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.v1 import deps
from app import models

router = APIRouter()

@router.get("/stats")
def get_system_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_admin), # Chỉ Admin được gọi
):
    """
    Lấy thống kê tổng quan: Tổng user, Tổng chat session, Tổng tin nhắn
    """
    total_users = db.query(models.User).count()
    total_sessions = db.query(models.ChatSession).count()
    total_messages = db.query(models.Message).count()
    
    # Lấy 5 user đăng ký gần nhất
    recent_users = db.query(models.User).order_by(models.User.id.desc()).limit(5).all()
    
    return {
        "total_users": total_users,
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "recent_users": recent_users
    }

@router.get("/users")
def get_all_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_admin),
):
    """Lấy danh sách toàn bộ user"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users