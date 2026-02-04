from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import llm

def sufficiency_checker_node(state):
    """
    Node 4: Kiểm tra thông minh
    Nhiệm vụ: Phân loại tình trạng dữ liệu (SUFFICIENT / MISSING_INFO / NO_LAW).
    """
    docs = state.get("retrieved_docs", [])
    query = state.get("standalone_query", state["query"])
    
    # TRƯỜNG HỢP 1: Không tìm thấy văn bản nào trong DB
    if not docs:
        print("🧠 [CHECKER]: Không tìm thấy luật -> NO_LAW")
        return {"check_status": "NO_LAW"}

    print("🧠 [CHECKER]: Đang kiểm tra mức độ đầy đủ...")
    context = "\n".join([f"- {d['content']}" for d in docs])

    # Prompt yêu cầu JSON
    prompt = PromptTemplate(
        template="""Bạn là Thẩm phán kiểm duyệt.
        
        Câu hỏi: {query}
        Căn cứ pháp lý tìm được:
        {context}

        Nhiệm vụ: Đánh giá xem có thể trả lời CHÍNH XÁC ngay lập tức không?
        
        Quy tắc:
        1. Nếu luật quy định chung chung hoặc chia nhiều trường hợp (ví dụ: "dưới 18 tuổi thì A, trên 18 thì B") mà người hỏi KHÔNG nói rõ -> "MISSING_INFO".
        2. Nếu luật đã rõ ràng và khớp hoàn toàn -> "SUFFICIENT".
        3. Nếu văn bản không liên quan -> "NO_LAW".

        Output JSON duy nhất:
        {{
            "status": "SUFFICIENT" | "MISSING_INFO" | "NO_LAW",
            "reason": "Giải thích ngắn gọn"
        }}
        """,
        input_variables=["query", "context"]
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    # --- SỬA LỖI TẠI ĐÂY ---
    try:
        result_json = chain.invoke({"query": query, "context": context})
        status = result_json.get("status", "NO_LAW")
        reason = result_json.get("reason", "Không rõ lý do")
    except Exception as e:
        print(f"⚠️ Lỗi Checker (JSON Parse): {e}")
        # Fallback an toàn nếu AI trả về lỗi định dạng
        status = "NO_LAW" 
        reason = "Lỗi định dạng JSON từ AI"
        
    print(f"   -> Đánh giá: {status} ({reason})")
    
    return {"check_status": status}