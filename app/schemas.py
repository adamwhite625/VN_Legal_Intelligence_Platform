from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# ==========================================
# 1. USER & AUTH SCHEMAS
# ==========================================
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    full_name: Optional[str] = None
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# ==========================================
# 2. DATABASE MODELS SCHEMAS (SESSION/MESSAGE)
# ==========================================
class MessageBase(BaseModel):
    sender: str
    message: str

class MessageCreate(MessageBase):
    session_id: int

class MessageResponse(MessageBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

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

# ==========================================
# 3. CHAT INTERACTION SCHEMAS
# ==========================================
class QueryInput(BaseModel):
    query: str
    session_id: Optional[int] = None 

class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []