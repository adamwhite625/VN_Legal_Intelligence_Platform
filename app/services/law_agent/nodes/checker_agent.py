from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.clients import get_llm
from app.services.law_agent.state import LawAgentState

def sufficiency_checker_node(state: LawAgentState) -> LawAgentState:
    llm = get_llm()
    print("🧠 [CHECKER]: Đang kiểm tra độ đầy đủ của thông tin...")
    
    query = state.standalone_query or state.query
    docs = state.retrieved_docs or []
    chat_history = state.chat_history or ""
    intent = state.intent or ""
    has_law_context = state.has_law_context  # Use the flag from contextualize
    
    # Content/definition questions that don't need specifics
    content_keywords = ["nội dung", "là gì", "định nghĩa", "khái niệm", "quy định", "quy định gì", "có nội dung gì", "bao gồm", "gồm những gì"]
    is_content_question = any(keyword in query.lower() for keyword in content_keywords)
    
    # If law context is available and it's a content question, mark as SUFFICIENT
    # The writer node will use the law context to answer
    if has_law_context and is_content_question:
        print(f"   -> Có ngữ cảnh luật + câu hỏi về nội dung → SUFFICIENT (sử dụng context)")
        state.check_status = "SUFFICIENT"
        state.node_trace.append("checker")
        return state
    
    # If law context is available and no docs were retrieved, mark as SUFFICIENT
    if has_law_context and not docs:
        print(f"   -> Có ngữ cảnh luật sẵn → SUFFICIENT (sử dụng context)")
        state.check_status = "SUFFICIENT"
        state.node_trace.append("checker")
        return state
    
    # ----------- LOGIC MỚI: Phân biệt MISSING_INFO vs NO_LAW -----------
    
    # 1. Query is vague only if extremely short (≤ 2 words)
    is_query_vague = len(query.split()) <= 2
    
    # 2. Nếu intent quá chung chung
    is_intent_generic = intent and intent in ["SEARCH_PENAL", "SEARCH_CIVIL"]
    
    # 3. Nếu không tìm thấy văn bản nào
    if not docs:
        # Nếu query mơ hồ HOẶC intent generic → MISSING_INFO (user cần phải cung cấp chi tiết hơn)
        if is_query_vague or is_intent_generic:
            print(f"   -> Query mơ hồ/intent chung chung → MISSING_INFO")
            state.check_status = "MISSING_INFO"
        else:
            # Query cụ thể nhưng không tìm được → NO_LAW
            print(f"   -> Query cụ thể nhưng không tìm được → NO_LAW")
            state.check_status = "NO_LAW"
        
        state.node_trace.append("checker")
        return state

    # --- LOGIC MỚI: Auto-sufficient cho SEARCH_PROCEDURE ---
    is_procedural = state.intent == "SEARCH_PROCEDURE"
    # 🧹 CLEAN: Chỉ tính từ từ dòng đầu tiên (loại bỏ "Dựa trên văn bản...")
    pure_query = (state.standalone_query or state.query).split("Dựa trên văn bản")[0].strip()
    if not pure_query:
        pure_query = (state.standalone_query or state.query).split("\n")[0].strip()
    query_words = len(pure_query.split())
    
    if is_procedural and query_words >= 4:
        print(f"   -> Procedural general query ({query_words} words) → SUFFICIENT (auto)")
        state.check_status = "SUFFICIENT"
        state.node_trace.append("checker")
        return state

    # Tạo context từ văn bản tìm được
    context_text = "\n\n".join([f"Văn bản: {d.law_name}\nNội dung: {d.content}" for d in docs])

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
        state.check_status = status
        state.node_trace.append("checker")
        return state
        
    except Exception as e:
        print(f"⚠️ Lỗi Checker: {e}")
        state.check_status = "SUFFICIENT"
        state.node_trace.append("checker")
        return state