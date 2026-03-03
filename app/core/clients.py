"""
Centralized initialization for external clients.

Production-ready:
- Config validation
- Collection validation
- Fail-fast strategy
"""

import logging
from typing import Optional
import time

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse, ResponseHandlingException
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.core import redis_client

logger = logging.getLogger(__name__)


_qdrant_client: Optional[QdrantClient] = None
_embeddings: Optional[HuggingFaceEmbeddings] = None
_llm: Optional[ChatOpenAI] = None


def init_clients() -> None:
    """
    Initialize external services.

    Must be called inside FastAPI lifespan startup.
    """

    global _qdrant_client, _embeddings, _llm

    # ---------------------------
    # Validate critical settings
    # ---------------------------

    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing in environment variables.")

    if not settings.COLLECTION_NAME:
        raise RuntimeError("COLLECTION_NAME is not configured.")

    # ---------------------------
    # Initialize Qdrant (with retry)
    # ---------------------------

    if _qdrant_client is None:
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                _qdrant_client = QdrantClient(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT,
                    timeout=5.0,
                )

                # Test connection
                collections = _qdrant_client.get_collections().collections
                collection_names = [c.name for c in collections]

                if settings.COLLECTION_NAME not in collection_names:
                    logger.warning(
                        f"Qdrant collection '{settings.COLLECTION_NAME}' does not exist. "
                        f"Available collections: {collection_names}"
                    )
                else:
                    logger.info(f"✓ Connected to Qdrant, found collection: {settings.COLLECTION_NAME}")
                
                break  # Successfully connected

            except (ResponseHandlingException, UnexpectedResponse, Exception) as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Qdrant connection attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                        f"Retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                else:
                    logger.error(
                        f"Failed to connect to Qdrant after {max_retries} attempts. "
                        f"Proceeding with JSON-based search only."
                    )
                    _qdrant_client = None  # Set to None so JSON search is used instead

    # ---------------------------
    # Initialize Embeddings
    # ---------------------------

    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )

    # ---------------------------
    # Initialize LLM
    # ---------------------------

    if _llm is None:
        _llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=settings.OPENAI_TEMPERATURE,
        )
        logger.info("✓ LLM initialized successfully")

    # ---------------------------
    # Initialize Redis
    # ---------------------------
    redis_client.init_redis()


def close_clients() -> None:
    """
    Gracefully close external resources.
    """
    redis_client.close_redis()
    logger.info("All clients closed")

def get_qdrant_client() -> QdrantClient:
    if _qdrant_client is None:
        raise RuntimeError("Qdrant client not initialized.")
    return _qdrant_client


def get_embeddings() -> HuggingFaceEmbeddings:
    if _embeddings is None:
        raise RuntimeError("Embeddings not initialized.")
    return _embeddings


def get_llm() -> ChatOpenAI:
    if _llm is None:
        raise RuntimeError("LLM not initialized.")
    return _llm
