from langgraph.graph import StateGraph, END
from app.core.agents.state import LawAgentState
from app.core.agents.router_agent import router_node
from app.core.agents.retrieval_agent import retriever_node
from app.core.agents.checker_agent import sufficiency_checker_node
from app.core.agents.writer_agent import answer_node
from app.core.agents.fallback_agent import fallback_node # Import file mới

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

# Logic rẽ nhánh mới
def route_after_check(state):
    status = state["check_status"]
    if status == "SUFFICIENT":
        return "answer"
    else:
        # Cả MISSING_INFO và NO_LAW đều đẩy sang Fallback xử lý
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