from langgraph.graph import StateGraph, END

# --- SỬA CÁC DÒNG IMPORT DƯỚI ĐÂY ---
# Import State từ cùng thư mục (dấu chấm .)
from .state import LawAgentState

# Import các Node từ thư mục con 'nodes'
from .nodes.router_agent import router_node
from .nodes.retrieval_agent import retriever_node
from .nodes.checker_agent import sufficiency_checker_node
from .nodes.writer_agent import answer_node
from .nodes.fallback_agent import fallback_node
# ------------------------------------

workflow = StateGraph(LawAgentState)

# Add Nodes
workflow.add_node("router", router_node)
workflow.add_node("retriever", retriever_node)
workflow.add_node("checker", sufficiency_checker_node)
workflow.add_node("answer", answer_node)
workflow.add_node("fallback", fallback_node)

# Edges
workflow.set_entry_point("router")
workflow.add_edge("router", "retriever")
workflow.add_edge("retriever", "checker")

# Logic rẽ nhánh
def route_after_check(state):
    status = state.get("check_status", "NO_LAW")
    if status == "SUFFICIENT":
        return "answer"
    else:
        # MISSING_INFO hoặc NO_LAW đều đẩy sang Fallback
        return "fallback"

workflow.add_conditional_edges(
    "checker",
    route_after_check,
    {
        "answer": "answer",
        "fallback": "fallback"
    }
)

workflow.add_edge("answer", END)
workflow.add_edge("fallback", END)

app = workflow.compile()