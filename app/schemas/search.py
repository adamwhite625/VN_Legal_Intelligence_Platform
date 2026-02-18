from pydantic import BaseModel
from typing import List, Optional


class LawItem(BaseModel):
    """Legal document item in search results"""
    id: Optional[str] = None
    title: str
    type: str
    year: Optional[str] = None
    authority: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    articles: Optional[List[str]] = None  # Danh sách số điều


class SearchQuery(BaseModel):
    """Search request"""
    keyword: str
    type: Optional[str] = None
    year: Optional[str] = None
    authority: Optional[str] = None


class SearchFilters(BaseModel):
    """Advanced search filters"""
    law_name: Optional[str] = None
    document_type: Optional[str] = None  # Luật, Nghị định, etc.
    article_number: Optional[str] = None
    year: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response"""
    results: List[LawItem]
    total: int
    filters_applied: Optional[SearchFilters] = None


class LawDetailResponse(BaseModel):
    """Law detail response"""
    id: str
    title: str
    type: str
    content: str
    year: Optional[str] = None
    authority: Optional[str] = None
    articles: Optional[List[str]] = None
