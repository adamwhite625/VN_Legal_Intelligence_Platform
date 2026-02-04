from typing import List
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import llm  # Import LLM từ file config vừa tạo

# ---------------------------------------------------------
# NODE 5: ANSWER GENERATOR (TRẢ LỜI KHI ĐỦ CĂN CỨ)
# ---------------------------------------------------------
def answer_node(state):
    print("🧠 [WRITER]: Đang soạn thảo câu trả lời...")
    
    docs = state["retrieved_docs"]
    query = state.get("standalone_query", state["query"])
    chat_history = state.get("chat_history", "")

    # 1. Trích xuất nguồn (Unique)
    unique_sources = list(set([d["source"] for d in docs]))
    
    # 2. Tạo context
    context_text = "\n\n".join([f"Nguồn: {d['source']}\nNội dung: {d['content']}" for d in docs])

    # 3. Prompt trả lời
    prompt = PromptTemplate(
        template="""Bạn là Luật sư AI chuyên nghiệp.
        
        Lịch sử trò chuyện:
        {chat_history}
        
        Thông tin pháp lý tìm được:
        {context}
        
        Câu hỏi của khách hàng: {query}
        
        Yêu cầu:
        1. Trả lời trực tiếp vào vấn đề.
        2. BẮT BUỘC trích dẫn điều luật (Ví dụ: "Theo Điều 56 Luật Hôn nhân...").
        3. Văn phong trang trọng, ấm áp, dễ hiểu.
        
        Lời tư vấn:""",
        input_variables=["chat_history", "context", "query"]
    )
    
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({
        "chat_history": chat_history,
        "context": context_text, 
        "query": query
    })
    
    return {
        "generation": answer,
        "sources": unique_sources
    }

# ---------------------------------------------------------
# NODE 6: SMART FALLBACK (HỎI LẠI HOẶC TỪ CHỐI)
# ---------------------------------------------------------
def fallback_node(state):
    print("🧠 [FALLBACK]: Kích hoạt quy trình xử lý thiếu thông tin...")
    
    status = state.get("check_status", "NO_LAW")
    query = state.get("standalone_query", state["query"])
    docs = state.get("retrieved_docs", [])
    
    # TRƯỜNG HỢP 1: KHÔNG TÌM THẤY LUẬT (NO_LAW) -> TỪ CHỐI THẲNG
    if status == "NO_LAW" or not docs:
        msg = (
            "Xin lỗi, hiện tại cơ sở dữ liệu của tôi chưa có văn bản pháp lý chính xác về vấn đề này. "
            "Để đảm bảo an toàn pháp lý, tôi xin phép không tự suy đoán. Bạn vui lòng tham vấn luật sư trực tiếp."
        )
        return {"generation": msg, "sources": []}

    # TRƯỜNG HỢP 2: CÓ LUẬT NHƯNG THIẾU THÔNG TIN USER (MISSING_INFO) -> HỎI LẠI
    if status == "MISSING_INFO":
        context_text = "\n".join([f"- {d['content']}" for d in docs])
        
        prompt = PromptTemplate(
            template="""Bạn là Luật sư tư vấn.
            Bạn đã tìm thấy quy định pháp luật liên quan, nhưng chưa thể áp dụng chính xác vì người hỏi cung cấp thiếu thông tin chi tiết.
            
            Văn bản luật tìm được:
            {context}
            
            Câu hỏi người dân: {query}
            
            Nhiệm vụ:
            Hãy viết câu phản hồi theo cấu trúc sau:
            1. Khẳng định vấn đề đã có quy định tại [Tên luật].
            2. Giải thích ngắn gọn tại sao chưa trả lời được ngay (Ví dụ: Luật chia thành nhiều trường hợp A, B, C...).
            3. Yêu cầu người dùng cung cấp thêm thông tin. Hãy liệt kê các câu hỏi cụ thể (gạch đầu dòng).
            
            Phản hồi:""",
            input_variables=["context", "query"]
        )
        
        chain = prompt | llm | StrOutputParser()
        clarification_msg = chain.invoke({"context": context_text, "query": query})
        
        # Vẫn trả về nguồn để user thấy mình có căn cứ
        unique_sources = list(set([d["source"] for d in docs]))
        
        return {
            "generation": clarification_msg,
            "sources": unique_sources
        }

    # Fallback an toàn cho các trường hợp lỗi lạ
    return {
        "generation": "Hệ thống đang gặp sự cố xác định trạng thái dữ liệu.",
        "sources": []
    }