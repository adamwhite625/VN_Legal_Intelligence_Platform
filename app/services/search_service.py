"""
Search service layer.
Handles full-text search in Qdrant vector database.
"""

import logging
from typing import List, Optional
from app.core.clients import get_qdrant_client, get_embeddings
from app.core.config import settings
from app.schemas.search import LawItem

logger = logging.getLogger(__name__)


async def search_laws(
    keyword: str,
    type_filter: Optional[str] = None,
    year_filter: Optional[str] = None,
    authority_filter: Optional[str] = None,
    limit: int = 20,
) -> List[LawItem]:
    """
    Search laws from Qdrant database.
    """
    try:
        qdrant = get_qdrant_client()
        embeddings = get_embeddings()

        # Embed query
        query_vector = embeddings.embed_query(keyword)

        # Search in Qdrant
        results = qdrant.query_points(
            collection_name=settings.COLLECTION_NAME,
            query=query_vector,
            limit=limit,
            with_payload=True,
        ).points

        laws: List[LawItem] = []

        for result in results:
            payload = result.payload or {}

            # Extract data from Qdrant payload
            law = LawItem(
                id=payload.get("so_hieu", ""),
                title=payload.get("loai_van_ban", ""),
                type=payload.get("loai_van_ban", "Văn bản"),
                content=payload.get("page_content") or payload.get("combine_Article_Content", ""),
                year=payload.get("nam", ""),
                authority=payload.get("co_quan_ban_hanh", ""),
                description=payload.get("tom_tat", ""),
            )

            # Apply filters
            if type_filter and type_filter.lower() not in law.type.lower():
                continue
            if year_filter and law.year != year_filter:
                continue
            if authority_filter and authority_filter.lower() not in (law.authority or "").lower():
                continue

            laws.append(law)

        return laws

    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        return []


async def get_law_detail(law_id: str) -> Optional[LawItem]:
    """
    Get detail of a specific law by ID (so_hieu).
    Search by law_id as keyword to find the exact law.
    """
    try:
        qdrant = get_qdrant_client()
        embeddings = get_embeddings()

        # Embed the law_id as query
        query_vector = embeddings.embed_query(law_id)

        # Search for the specific law in Qdrant
        results = qdrant.query_points(
            collection_name=settings.COLLECTION_NAME,
            query=query_vector,
            limit=10,
            with_payload=True,
        ).points

        if not results:
            return None

        # Find exact match by so_hieu
        for result in results:
            payload = result.payload or {}
            if payload.get("so_hieu", "").strip().lower() == law_id.strip().lower():
                return LawItem(
                    id=payload.get("so_hieu", ""),
                    title=payload.get("loai_van_ban", ""),
                    type=payload.get("loai_van_ban", "Văn bản"),
                    content=payload.get("page_content") or payload.get("combine_Article_Content", ""),
                    year=payload.get("nam", ""),
                    authority=payload.get("co_quan_ban_hanh", ""),
                    description=payload.get("tom_tat", ""),
                )

        # If no exact match, return the best match
        if results:
            payload = results[0].payload or {}
            return LawItem(
                id=payload.get("so_hieu", ""),
                title=payload.get("loai_van_ban", ""),
                type=payload.get("loai_van_ban", "Văn bản"),
                content=payload.get("page_content") or payload.get("combine_Article_Content", ""),
                year=payload.get("nam", ""),
                authority=payload.get("co_quan_ban_hanh", ""),
                description=payload.get("tom_tat", ""),
            )

        return None

    except Exception as e:
        logger.error(f"Get law detail error: {str(e)}", exc_info=True)
        return None

