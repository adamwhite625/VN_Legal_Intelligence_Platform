"""
JSON-based law search service for fast lookup.
Loads law data from JSON file into memory for instant search.
"""

import json
import logging
from typing import List, Optional
from pathlib import Path
from app.schemas.search import LawItem

logger = logging.getLogger(__name__)

# Singleton cache for loaded JSON data
_json_data_cache = None
_json_file_path = None


def _get_json_file_path() -> Path:
    """Get the path to the raw law data JSON file."""
    return Path(__file__).parent.parent / "core" / "raw_law_data.json"


def load_json_data():
    """Load law data from JSON file into memory."""
    global _json_data_cache
    
    if _json_data_cache is not None:
        return _json_data_cache
    
    try:
        file_path = _get_json_file_path()
        
        if not file_path.exists():
            logger.warning(f"JSON file not found: {file_path}")
            return []
        
        with open(file_path, "r", encoding="utf-8") as f:
            _json_data_cache = json.load(f)
            logger.info(f"Loaded {len(_json_data_cache)} laws from JSON file")
            return _json_data_cache
    
    except Exception as e:
        logger.error(f"Error loading JSON data: {str(e)}", exc_info=True)
        return []


def search_json_laws(
    keyword: str,
    type_filter: Optional[str] = None,
    year_filter: Optional[str] = None,
    authority_filter: Optional[str] = None,
    limit: int = 20,
) -> List[LawItem]:
    """
    Fast search in JSON data by keyword (title, content, law_name).
    Returns exact matches and partial matches.
    """
    try:
        data = load_json_data()
        
        if not data:
            return []
        
        results: List[LawItem] = []
        keyword_lower = keyword.lower()
        
        # Track unique laws to avoid duplicates (same law can have multiple articles)
        seen_laws = set()
        
        for item in data:
            # Extract fields from JSON
            article_id = item.get("article_id", "")
            article_title = item.get("article_title", "")
            content = item.get("content", "")
            law_name = item.get("law_name", "")
            
            # Search in article_title, law_name, and content
            title_match = keyword_lower in article_title.lower()
            name_match = keyword_lower in law_name.lower()
            content_match = keyword_lower in content.lower()
            
            if not (title_match or name_match or content_match):
                continue
            
            # Create unique key for this law
            law_key = f"{article_id}_{law_name}"
            
            if law_key in seen_laws:
                continue
            seen_laws.add(law_key)
            
            law = LawItem(
                id=article_id,
                title=law_name,
                type="Luật",  # Default type from JSON
                year=None,    # Not available in raw_law_data.json
                authority=None,  # Not available in raw_law_data.json
                description=article_title[:200],  # First 200 chars as description
                content=content,
            )
            
            results.append(law)
            
            if len(results) >= limit:
                break
        
        logger.info(f"JSON search for '{keyword}' returned {len(results)} results")
        return results
    
    except Exception as e:
        logger.error(f"JSON search error: {str(e)}", exc_info=True)
        return []


def get_json_law_detail(law_id: str) -> Optional[LawItem]:
    """
    Get detail of a law by article_id from JSON.
    """
    try:
        data = load_json_data()
        
        if not data:
            return None
        
        # Search for the article by article_id
        for item in data:
            if item.get("article_id", "").lower() == law_id.lower():
                law = LawItem(
                    id=item.get("article_id", ""),
                    title=item.get("law_name", ""),
                    type="Luật",
                    year=None,
                    authority=None,
                    description=item.get("article_title", ""),
                    content=item.get("content", ""),
                )
                return law
        
        logger.info(f"Law detail not found for ID: {law_id}")
        return None
    
    except Exception as e:
        logger.error(f"Get law detail error: {str(e)}", exc_info=True)
        return None

