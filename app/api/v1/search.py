from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, Literal
from sqlalchemy.orm import Session

from app.schemas.search import SearchQuery, SearchResponse, LawDetailResponse
from app.services.search_service import search_laws, get_law_detail
from app.services.json_search_service import search_json_laws, get_json_law_detail
from app.services.tracking_service import TrackingService
from app.utils.slug_generator import create_law_slug
from app import models
from app.api.v1 import deps

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search(
    keyword: str = Query(..., min_length=1),
    mode: Literal["fast", "semantic"] = Query("fast", description="fast=JSON file, semantic=Qdrant"),
    type_filter: Optional[str] = Query(None, description="Loại văn bản (Luật, Nghị định, etc.)"),
    year_filter: Optional[str] = Query(None, description="Năm ban hành"),
    authority_filter: Optional[str] = Query(None, description="Cơ quan ban hành"),
    article_filter: Optional[str] = Query(None, description="Số điều"),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Search for laws with advanced filters
    
    Supports:
    - Keyword search
    - Filter by document type (Luật, Nghị định, etc.)
    - Filter by year
    - Filter by authority
    - Filter by article number
    """
    try:
        if mode == "fast":
            results = search_json_laws(
                keyword=keyword,
                type_filter=type_filter,
                year_filter=year_filter,
                authority_filter=authority_filter,
                limit=limit,
            )
        else:  # semantic
            results = await search_laws(
                keyword=keyword,
                type_filter=type_filter,
                year_filter=year_filter,
                authority_filter=authority_filter,
                limit=limit,
            )

        return SearchResponse(
            results=results,
            total=len(results),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/laws/{law_id}", response_model=LawDetailResponse)
async def get_law(
    law_id: str,
    source: Literal["auto", "json", "qdrant"] = Query("auto", description="Where to fetch from"),
    db: Session = Depends(deps.get_db),
):
    """
    Get detail of a specific law by ID or slug
    Supports both law_id (e.g., "Điều 1") and slug (e.g., "dieu-1", "dieu-1-pham-vi-dieu-chinh")
    """
    try:
        law = None
        actual_law_id = law_id
        
        # Try to lookup by slug first if it looks like a slug (contains hyphens and lowercase)
        if "-" in law_id and law_id.islower():
            # This looks like a slug, try to find it in database
            saved_law = db.query(models.SavedLaw).filter(
                models.SavedLaw.slug == law_id
            ).first()
            if saved_law:
                actual_law_id = saved_law.law_id
        
        if source == "json":
            law = get_json_law_detail(actual_law_id)
        elif source == "qdrant":
            law = await get_law_detail(actual_law_id)
        else:  # auto
            law = get_json_law_detail(actual_law_id)
            if not law:
                law = await get_law_detail(actual_law_id)

        if not law:
            raise HTTPException(status_code=404, detail="Law not found")

        return LawDetailResponse(
            id=law.id,
            title=law.title,
            type=law.type,
            content=law.content,
            year=law.year,
            authority=law.authority,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/laws/{law_id}/save")
async def save_law_and_create_session(
    law_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Save a law and create a law-detail session for it
    Returns the saved law with slug for URL usage
    """
    try:
        # Lấy law detail
        law = get_json_law_detail(law_id)
        if not law:
            law = await get_law_detail(law_id)
        
        if not law:
            raise HTTPException(status_code=404, detail="Law not found")
        
        # Save law (with slug generation)
        saved_law = TrackingService.save_law(
            db=db,
            user_id=current_user.id,
            law_id=law.id,
            law_title=law.title,
            law_type=law.type,
            law_year=law.year,
            law_authority=law.authority,
            law_content=law.content,
        )
        
        # Create law-detail session
        session = models.ChatSession(
            user_id=current_user.id,
            session_type="law-detail",
            law_id=law_id,
            title=f"Chat về {law.title}",
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return {
            "message": "Law saved successfully",
            "saved_law_id": saved_law.id,
            "slug": saved_law.slug,
            "session_id": session.id,
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

