"""
Redis client initialization and utilities.

Supports:
- Caching search results
- Session storage
- Token blacklist
- Rate limiting data
"""

import logging
import json
from typing import Any, Optional
from redis import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis client
_redis_client: Optional[Redis] = None


def init_redis() -> Optional[Redis]:
    """Initialize Redis client."""
    global _redis_client
    
    if _redis_client is not None:
        return _redis_client
    
    try:
        _redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
        )
        
        # Test connection
        _redis_client.ping()
        logger.info(f"✓ Redis connected: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        return _redis_client
        
    except Exception as e:
        logger.error(f"✗ Redis connection failed: {str(e)}")
        _redis_client = None
        return None


def get_redis() -> Optional[Redis]:
    """Get Redis client instance."""
    global _redis_client
    
    if _redis_client is None:
        return init_redis()
    
    return _redis_client


def close_redis():
    """Close Redis connection."""
    global _redis_client
    
    if _redis_client is not None:
        try:
            _redis_client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis: {str(e)}")
        finally:
            _redis_client = None


# ============================================
# CACHE UTILITIES
# ============================================

def cache_get(key: str) -> Optional[Any]:
    """Get value from cache."""
    try:
        redis = get_redis()
        if not redis:
            return None
        
        value = redis.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None
    except Exception as e:
        logger.warning(f"Cache get error: {str(e)}")
        return None


def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    """Set value in cache with TTL (seconds)."""
    try:
        redis = get_redis()
        if not redis:
            return False
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        return redis.setex(key, ttl, value) is not None
    except Exception as e:
        logger.warning(f"Cache set error: {str(e)}")
        return False


def cache_delete(key: str) -> bool:
    """Delete key from cache."""
    try:
        redis = get_redis()
        if not redis:
            return False
        
        return redis.delete(key) > 0
    except Exception as e:
        logger.warning(f"Cache delete error: {str(e)}")
        return False


def cache_exists(key: str) -> bool:
    """Check if key exists in cache."""
    try:
        redis = get_redis()
        if not redis:
            return False
        
        return redis.exists(key) > 0
    except Exception as e:
        logger.warning(f"Cache exists error: {str(e)}")
        return False


def cache_clear_pattern(pattern: str) -> int:
    """Clear all keys matching pattern."""
    try:
        redis = get_redis()
        if not redis:
            return 0
        
        keys = redis.keys(pattern)
        if keys:
            return redis.delete(*keys)
        return 0
    except Exception as e:
        logger.warning(f"Cache clear pattern error: {str(e)}")
        return 0


# ============================================
# SESSION UTILITIES
# ============================================

def session_set(user_id: int, session_data: dict, ttl: int = 86400) -> bool:
    """Set session data (24 hours by default)."""
    key = f"session:{user_id}"
    return cache_set(key, session_data, ttl)


def session_get(user_id: int) -> Optional[dict]:
    """Get session data."""
    key = f"session:{user_id}"
    return cache_get(key)


def session_delete(user_id: int) -> bool:
    """Delete session."""
    key = f"session:{user_id}"
    return cache_delete(key)


# ============================================
# TOKEN BLACKLIST UTILITIES
# ============================================

def token_blacklist(token: str, ttl: int = 3600) -> bool:
    """Add token to blacklist (logout, revoke)."""
    key = f"token_blacklist:{token}"
    return cache_set(key, "1", ttl)


def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted."""
    key = f"token_blacklist:{token}"
    return cache_exists(key)


# ============================================
# SEARCH CACHE UTILITIES
# ============================================

def cache_search_results(keyword: str, mode: str, results: list, ttl: int = 3600) -> bool:
    """Cache search results."""
    key = f"search:{mode}:{keyword}"
    return cache_set(key, results, ttl)


def get_cached_search(keyword: str, mode: str) -> Optional[list]:
    """Get cached search results."""
    key = f"search:{mode}:{keyword}"
    return cache_get(key)


def clear_search_cache(mode: str = "*") -> int:
    """Clear search cache."""
    pattern = f"search:{mode}:*"
    return cache_clear_pattern(pattern)


# ============================================
# COUNTER UTILITIES (for rate limiting, etc.)
# ============================================

def increment_counter(key: str, ttl: int = 60) -> int:
    """Increment counter, useful for rate limiting."""
    try:
        redis = get_redis()
        if not redis:
            return 0
        
        value = redis.incr(key)
        if value == 1:
            redis.expire(key, ttl)
        return value
    except Exception as e:
        logger.warning(f"Counter increment error: {str(e)}")
        return 0


def get_counter(key: str) -> int:
    """Get counter value."""
    try:
        redis = get_redis()
        if not redis:
            return 0
        
        value = redis.get(key)
        return int(value) if value else 0
    except Exception as e:
        logger.warning(f"Counter get error: {str(e)}")
        return 0


def reset_counter(key: str) -> bool:
    """Reset counter."""
    return cache_delete(key)
