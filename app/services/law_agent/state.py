"""
Typed Agent State for Legal Agentic RAG.

Production-ready version with:
- strict schema
- deterministic fields
- typed documents
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ==========================================================
# Retrieved Document Schema
# ==========================================================

class RetrievedDocument(BaseModel):
    """
    Structured representation of a retrieved legal document.
    """

    law_id: str
    law_name: str
    content: str
    score: float


# ==========================================================
# Agent State Schema
# ==========================================================

class LawAgentState(BaseModel):
    """
    Complete state of the Legal Agent during reasoning.
    """

    # ----------------------
    # Input
    # ----------------------
    query: str
    standalone_query: Optional[str] = None
    chat_history: Optional[str] = None
    has_law_context: bool = False  # Track if law context is present
    law_context: Optional[str] = None  # Store extracted law context

    # ----------------------
    # Router Reasoning
    # ----------------------
    intent: Optional[str] = None
    search_limit: Optional[int] = None

    # ----------------------
    # Retrieval
    # ----------------------
    retrieved_docs: List[RetrievedDocument] = Field(default_factory=list)

    # ----------------------
    # Sufficiency Check
    # ----------------------
    check_status: Optional[
        Literal["SUFFICIENT", "MISSING_INFO", "NO_LAW"]
    ] = None

    # ----------------------
    # Output
    # ----------------------
    generation: Optional[str] = None
    sources: List[str] = Field(default_factory=list)

    # ----------------------
    # Observability
    # ----------------------
    error_message: Optional[str] = None
    node_trace: List[str] = Field(default_factory=list)
