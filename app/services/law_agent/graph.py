"""
LangGraph workflow for Legal Agentic RAG.

Production-ready version with:
- strict routing
- safe state handling
- deterministic branching
"""

from langgraph.graph import StateGraph, END
from typing import Literal

from .state import LawAgentState

# Import nodes
from .nodes.contextualize_agent import contextualize_node
from .nodes.router_agent import router_node
from .nodes.retrieval_agent import retriever_node
from .nodes.checker_agent import sufficiency_checker_node
from .nodes.writer_agent import answer_node
from .nodes.fallback_agent import fallback_node
from .nodes.clarifier_agent import clarifier_node
from .nodes.web_search_agent import web_search_node

# ==========================================================
# Graph Definition
# ==========================================================

workflow = StateGraph(LawAgentState)


# ----------------------
# Register Nodes
# ----------------------

workflow.add_node("contextualize", contextualize_node)
workflow.add_node("router", router_node)
workflow.add_node("retriever", retriever_node)
workflow.add_node("web_search", web_search_node)
workflow.add_node("checker", sufficiency_checker_node)
workflow.add_node("answer", answer_node)
workflow.add_node("fallback", fallback_node)
workflow.add_node("clarifier", clarifier_node)



# ----------------------
# Entry Point
# ----------------------

workflow.set_entry_point("contextualize")


# ----------------------
# Router & Retrieval Routing
# ----------------------

workflow.add_edge("contextualize", "router")


def route_after_router(state: LawAgentState) -> Literal["retriever", "web_search", "fallback"]:
    """
    Route to local vector search, live web search, or fallback.
    """
    if state.intent == "SEARCH_WEB":
        return "web_search"
    if state.intent == "NO_SEARCH":
        return "fallback"
    return "retriever"


workflow.add_conditional_edges(
    "router",
    route_after_router,
    {
        "retriever": "retriever",
        "web_search": "web_search",
        "fallback": "fallback",
    },
)

workflow.add_edge("retriever", "checker")
workflow.add_edge("web_search", "checker")


# ----------------------
# Conditional Branching
# ----------------------

def route_after_check(state: LawAgentState) -> Literal["answer", "clarifier", "fallback"]:
    """
    Decide next node based on sufficiency check.

    Routing logic:
    - SUFFICIENT → answer node
    - MISSING_INFO → clarifier node
    - NO_LAW or others → fallback node
    """

    if state.check_status is None:
        return "fallback"

    if state.check_status == "SUFFICIENT":
        return "answer"

    if state.check_status == "MISSING_INFO":
        return "clarifier"

    return "fallback"


workflow.add_conditional_edges(
    "checker",
    route_after_check,
    {
        "answer": "answer",
        "clarifier": "clarifier",
        "fallback": "fallback",
    },
)


# ----------------------
# Terminal Edges
# ----------------------

workflow.add_edge("answer", END)
workflow.add_edge("clarifier", END)
workflow.add_edge("fallback", END)


# ==========================================================
# Compile
# ==========================================================

app = workflow.compile()
