from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.clients import get_llm
from app.services.law_agent.state import LawAgentState

def router_node(state: LawAgentState) -> LawAgentState:
    """Node 1: Router Agent - Điều hướng và xác định số lượng tài liệu cần tìm"""
    llm = get_llm()
    query = state.standalone_query or state.query
    print(f"🧠 [ROUTER]: Phân tích hướng đi cho '{query}'...")

    prompt = PromptTemplate(
        template="""Bạn là Router điều hướng câu hỏi pháp lý.
        Nhiệm vụ: Phân loại câu hỏi và xác định số lượng văn bản luật cần tìm (limit).
        
        QUY TẮC PHÂN LOẠI & LIMIT (Cập nhật):
        
        1. "SEARCH_PENAL": Hình sự (Giết người, trộm cắp, ma túy, đánh nhau, án tù...).
           - Đặc điểm: Vector Search thường bị nhiễu bởi các điều luật về hình phạt chung (án treo, tử hình...).
           - YÊU CẦU ĐẶC BIỆT: Set limit = 10 (Phải lấy rộng để chắc chắn bắt được đúng Điều luật cụ thể).
           
        2. "SEARCH_CIVIL": Dân sự (Đất đai, hợp đồng, bồi thường, thừa kế...).
           - Yêu cầu: Set limit = 5
           
        3. "SEARCH_PROCEDURE": Thủ tục tố tụng/Hành chính (Nộp đơn ở đâu, hồ sơ gồm gì...).
           - Yêu cầu: Set limit = 4
           
        4. "SEARCH_MARRIAGE": Hôn nhân gia đình.
           - Yêu cầu: Set limit = 4
           
        5. "SEARCH_WEB": Luật quốc tế, tin tức pháp lý mới, hoặc câu hỏi ngoài cơ sở dữ liệu luật Việt Nam.
           - Yêu cầu: Set limit = 0

        6. "NO_SEARCH": Xã giao (Chào bạn), câu hỏi vô nghĩa hoặc không liên quan luật.
           - Yêu cầu: Set limit = 0

        Câu hỏi: {query}
        
        Trả về JSON duy nhất (Không giải thích):
        {{
            "intent": "SEARCH_PENAL" | "SEARCH_CIVIL" | "SEARCH_PROCEDURE" | "SEARCH_MARRIAGE" | "SEARCH_WEB" | "NO_SEARCH",
            "limit": <số nguyên>
        }}
        """,
        input_variables=["query"],
    )
    
    chain = prompt | llm | JsonOutputParser()
    try:
        decision = chain.invoke({"query": query})
    except Exception as e:
        print(f"⚠️ Lỗi Router: {e}")
        # Fallback an toàn: Nếu lỗi thì mặc định tìm Hình sự với limit 10
        decision = {"intent": "SEARCH_PENAL", "limit": 10}

    state.intent = decision.get("intent", "SEARCH_PENAL")
    state.search_limit = decision.get("limit", 10)
    
    print(f"   -> Quyết định: {decision}")
    state.node_trace.append("router")
    return state