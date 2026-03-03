from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SessionResponse(BaseModel):
    id: int
    session_type: str  # "general" hoặc "law-detail"
    law_id: Optional[str] = None
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
