from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import llm

def router_node(state):
    """Node 1: Router Agent"""
    query = state.get("standalone_query", state["query"])
    print(f"🧠 [ROUTER]: Phân tích hướng đi cho '{query}'...")

    prompt = PromptTemplate(
        template="""Bạn là Router điều hướng câu hỏi pháp lý.
        Phân loại câu hỏi vào một trong các nhóm sau:
        
        - "SEARCH_PENAL": Hỏi về mức PHẠT tiền, phạt tù, tội danh, vi phạm GIAO THÔNG, trật tự xã hội.
        - "SEARCH_PROCEDURE": Hỏi về THỦ TỤC, hồ sơ, giấy tờ, nơi nộp đơn, quy trình tòa án.
        - "SEARCH_CIVIL": Hỏi về ly hôn, quyền nuôi con, đất đai, thừa kế, hợp đồng dân sự.
        - "NO_SEARCH": Câu hỏi xã giao (Chào bạn, who are you) hoặc không liên quan luật.

        Trả về JSON duy nhất:
        {{
            "intent": "SEARCH_PENAL" | "SEARCH_PROCEDURE" | "SEARCH_CIVIL" | "NO_SEARCH",
            "limit": <số lượng văn bản (int)>
        }}
        
        Quy tắc limit:
        - SEARCH_PENAL: 3
        - SEARCH_PROCEDURE: 5
        - SEARCH_CIVIL: 4
        - NO_SEARCH: 0

        Câu hỏi: {query}
        """,
        input_variables=["query"],
    )
    
    chain = prompt | llm | JsonOutputParser()
    try:
        decision = chain.invoke({"query": query})
    except Exception as e:
        print(f"⚠️ Lỗi Router: {e}")
        # Fallback an toàn, nhưng logic hơn: Mặc định tìm 3 văn bản
        decision = {"intent": "SEARCH_CIVIL", "limit": 3}

    print(f"   -> Quyết định: {decision}")
    
    return {
        "intent": decision.get("intent", "SEARCH_CIVIL"),
        "search_limit": decision.get("limit", 3)
    }