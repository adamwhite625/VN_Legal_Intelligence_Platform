from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import llm

# Định nghĩa cấu trúc JSON đầu ra
# (Mẹo: Định nghĩa class Pydantic để parser chính xác hơn, nhưng dùng prompt text cũng ổn với GPT-4)
def sufficiency_checker_node(state):
    print("🧠 [CHECKER]: Đang kiểm tra độ đầy đủ của thông tin...")
    
    query = state.get("standalone_query", state["query"])
    docs = state.get("retrieved_docs", [])
    chat_history = state.get("chat_history", "")
    
    # Nếu không tìm thấy văn bản nào -> NO_LAW
    if not docs:
        return {"check_status": "NO_LAW"}

    # Tạo context từ văn bản tìm được
    context_text = "\n\n".join([f"Văn bản: {d['source']}\nNội dung: {d['content']}" for d in docs])

    # --- PROMPT ĐƯỢC NÂNG CẤP ("KHÓ TÍNH" HƠN) ---
    checker_prompt = PromptTemplate(
        template="""Bạn là một Thẩm phán cấp cao, cực kỳ kỹ tính. Nhiệm vụ của bạn là đánh giá xem thông tin hiện tại ĐÃ ĐỦ để đưa ra phán quyết (câu trả lời) chính xác cho người dùng hay chưa.

        1. CÂU HỎI CỦA NGƯỜI DÙNG: "{query}"
        
        2. LỊCH SỬ TRÒ CHUYỆN (Context):
        {chat_history}

        3. VĂN BẢN PHÁP LUẬT TÌM ĐƯỢC:
        {context}

        --- TIÊU CHÍ ĐÁNH GIÁ (QUAN TRỌNG) ---
        
        TRƯỜNG HỢP 1: MISSING_INFO (Thiếu thông tin chi tiết)
        - Nếu văn bản luật quy định nhiều khung hình phạt khác nhau dựa trên các yếu tố định lượng (Ví dụ: giá trị tài sản, tỷ lệ thương tật, có tổ chức hay không...).
        - VÀ người dùng CHƯA cung cấp các con số/chi tiết đó trong câu hỏi hoặc lịch sử chat.
        - Ví dụ: Hỏi "Trộm cắp bị phạt bao nhiêu năm?" -> Luật có khung 6 tháng-3 năm, 2-7 năm, 7-15 năm tùy số tiền -> Người dùng chưa nói số tiền -> MISSING_INFO.
        
        TRƯỜNG HỢP 2: SUFFICIENT (Đủ thông tin)
        - Nếu câu hỏi chỉ mang tính định nghĩa, khái niệm (VD: "Thế nào là ly hôn?").
        - HOẶC người dùng ĐÃ cung cấp đủ tình tiết khớp với một khoản cụ thể trong luật.
        - HOẶC luật chỉ có 1 mức phạt duy nhất không phụ thuộc điều kiện.
        
        TRƯỜNG HỢP 3: NO_LAW (Sai luật/Không liên quan)
        - Văn bản tìm được hoàn toàn không liên quan đến câu hỏi.

        --- YÊU CẦU ĐẦU RA (JSON) ---
        Chỉ trả về JSON duy nhất, không giải thích thêm:
        {{
            "status": "SUFFICIENT" | "MISSING_INFO" | "NO_LAW",
            "reason": "Giải thích ngắn gọn tại sao (Ví dụ: Cần biết giá trị tài sản để xác định khung hình phạt)"
        }}
        """,
        input_variables=["query", "chat_history", "context"]
    )

    chain = checker_prompt | llm | JsonOutputParser()

    try:
        result = chain.invoke({
            "query": query,
            "chat_history": chat_history, 
            "context": context_text
        })
        
        status = result.get("status", "NO_LAW")
        reason = result.get("reason", "")
        
        print(f"   -> Đánh giá: {status} ({reason})")
        
        return {"check_status": status}
        
    except Exception as e:
        print(f"⚠️ Lỗi Checker: {e}")
        # Mặc định cho là đủ để Writer xử lý nếu lỗi
        return {"check_status": "SUFFICIENT"}