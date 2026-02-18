from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ============= SAVED LAWS =============

class SavedLawCreate(BaseModel):
    """Create a saved law"""
    law_id: str
    law_title: str
    law_type: Optional[str] = None
    law_year: Optional[str] = None
    law_authority: Optional[str] = None
    law_content: Optional[str] = None
    notes: Optional[str] = None


class SavedLawResponse(BaseModel):
    """Response for saved law"""
    id: int
    law_id: str
    law_title: str
    law_type: Optional[str] = None
    law_year: Optional[str] = None
    law_authority: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============= SAVED QUESTIONS =============

class SavedQuestionCreate(BaseModel):
    """Create a saved question"""
    question: str
    answer: Optional[str] = None
    law_id: Optional[str] = None
    tags: Optional[List[str]] = None


class SavedQuestionUpdate(BaseModel):
    """Update a saved question"""
    answer: Optional[str] = None
    tags: Optional[List[str]] = None
    is_bookmarked: Optional[bool] = None


class SavedQuestionResponse(BaseModel):
    """Response for saved question"""
    id: int
    question: str
    answer: Optional[str] = None
    law_id: Optional[str] = None
    tags: Optional[List[str]] = None
    is_bookmarked: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============= USER TRACKING =============

class UserTrackingStats(BaseModel):
    """User tracking statistics"""
    total_saved_laws: int
    total_saved_questions: int
    total_sessions: int
    recent_sessions: List[dict]


# ============= SEARCH WITH FILTERS =============

class SearchFilters(BaseModel):
    """Advanced search filters"""
    law_name: Optional[str] = None
    document_type: Optional[str] = None  # Luật, Nghị định, etc.
    article_number: Optional[str] = None
    year: Optional[str] = None


