from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class QueryInput(BaseModel):
    query: str
    session_id: Optional[int] = None
    context_type: str = "general"  # "general" hoặc "law-detail"
    law_id: Optional[str] = None  # Dùng khi context_type="law-detail"


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    session_id: int
    message_id: int


class MessageWithContext(BaseModel):
    """Message với context"""
    id: int
    sender: str  # user hoặc assistant
    message: str
    sources: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SessionHistory(BaseModel):
    """Chat session history"""
    id: int
    session_type: str  # "general" hoặc "law-detail"
    law_id: Optional[str] = None
    title: Optional[str] = None
    messages: List[MessageWithContext]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageSummaryResponse(BaseModel):
    """Message summary"""
    id: int
    summary: str
    message_count: int
    summarized_at: datetime

    class Config:
        from_attributes = True
