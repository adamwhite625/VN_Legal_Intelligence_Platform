from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# --- Session Schemas ---
class SessionBase(BaseModel):
    pass

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: int
    created_at: datetime
    first_message: Optional[str] = None # Để hiển thị preview tin nhắn đầu tiên ở sidebar

    class Config:
        from_attributes = True  # Cho phép đọc dữ liệu từ SQLAlchemy model

# --- Message Schemas ---
class MessageBase(BaseModel):
    sender: str  # "user" hoặc "bot"
    message: str

class MessageCreate(MessageBase):
    session_id: int

class MessageResponse(MessageBase):
    id: int
    session_id: int
    sent_at: datetime

    class Config:
        from_attributes = True