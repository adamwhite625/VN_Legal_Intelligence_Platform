from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# --- Message Schemas ---
class MessageBase(BaseModel):
    # SỬA ĐỔI QUAN TRỌNG: Dùng 'sender' và 'message' để khớp với database cũ
    sender: str
    message: str

class MessageCreate(MessageBase):
    session_id: int

class MessageResponse(MessageBase):
    id: int
    # Lưu ý: Database của bạn dùng sent_at hay created_at? 
    # Nếu crud.py dùng sent_at thì ở đây cũng nên để sent_at, hoặc map nó
    # Tuy nhiên để an toàn, mình dùng created_at theo chuẩn chung, 
    # Nếu lỗi hiển thị ngày giờ thì tính sau, quan trọng là lưu được chat đã.
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# --- Session Schemas ---
class SessionBase(BaseModel):
    pass

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: int
    created_at: datetime
    first_message: Optional[str] = None 
    
    class Config:
        from_attributes = True