"""
Contextualization node for Agentic Legal RAG.

Handles:
- Standalone query rewriting
- Clarification merging
"""

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.clients import get_llm
from app.services.law_agent.state import LawAgentState


def contextualize_node(state: LawAgentState) -> LawAgentState:

    state.node_trace.append("contextualize")

    query = state.query.strip()
    
    # 🧹 FIRST: Detect law context and extract it BEFORE cleaning the query
    # This preserves the law context in state for later use
    has_law_context = "Ngữ cảnh luật:" in query or "Nội dung:" in query
    state.has_law_context = has_law_context
    
    # Extract and store law context for writer/fallback nodes
    if has_law_context:
        if "Ngữ cảnh luật:" in query:
            parts = query.split("Ngữ cảnh luật:", 1)
            if len(parts) > 1:
                # Get law context up to the next major section
                context_part = parts[1].split("Lịch sử chat:")[0].split("Câu hỏi")[0]
                state.law_context = "Ngữ cảnh luật:" + context_part.strip()
    
    # Now extract the actual question from the combined prompt
    # Handle both law-detail and general formats
    
    # For law-detail format: extract from "Câu hỏi hiện tại:" or "Câu hỏi:"
    if "Câu hỏi hiện tại:" in query:
        parts = query.split("Câu hỏi hiện tại:", 1)
        pure_query = parts[1].split("\n")[0].strip() if len(parts) > 1 else ""
    elif "Câu hỏi:" in query:
        parts = query.split("Câu hỏi:", 1)
        pure_query = parts[1].split("\n")[0].strip() if len(parts) > 1 else ""
    else:
        # Fallback: clean query by removing "Dựa trên văn bản..." section
        pure_query = query.split("Dựa trên văn bản")[0].strip()
        if not pure_query:
            pure_query = query.split("\n")[0].strip()
    
    # If still empty, use full query
    if not pure_query:
        pure_query = query
    
    # Update state.query with cleaned version so all downstream nodes get clean query
    state.query = pure_query
    
    chat_history = state.chat_history or ""

    # If there is chat history, rewrite as standalone
    if chat_history:

        llm = get_llm()

        prompt = PromptTemplate(
            template="""
Dựa trên lịch sử hội thoại dưới đây,
hãy viết lại câu hỏi cuối cùng của người dùng
thành một câu hỏi pháp lý đầy đủ, rõ nghĩa.

Lịch sử:
{chat_history}

Câu hỏi mới:
{query}

Câu hỏi đầy đủ:
""",
            input_variables=["chat_history", "query"],
        )

        chain = prompt | llm | StrOutputParser()

        try:
            standalone = chain.invoke({
                "chat_history": chat_history,
                "query": pure_query  # Use cleaned query for rewrite
            })

            # Clean the rewritten query again
            pure_standalone = standalone.split("Dựa trên văn bản")[0].strip()
            if not pure_standalone:
                pure_standalone = standalone.split("\n")[0].strip()
            
            if not pure_standalone:
                pure_standalone = standalone.strip()
            
            state.standalone_query = pure_standalone
            return state

        except Exception:
            state.standalone_query = pure_query
            return state

    # No history → use cleaned query as standalone
    state.standalone_query = pure_query
    return state
