from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import llm

def answer_node(state):
    print("✍️ [WRITER]: Đang soạn thảo câu trả lời...")
    
    docs = state.get("retrieved_docs", [])
    query = state.get("standalone_query", state["query"])
    chat_history = state.get("chat_history", "")

    # 1. Trích xuất nguồn (Unique)
    unique_sources = list(set([d["source"] for d in docs]))
    
    # 2. Tạo context
    context_text = "\n\n".join([f"Nguồn: {d['source']}\nNội dung: {d['content']}" for d in docs])

    # 3. Prompt (ĐÃ CẬP NHẬT ĐỂ TRÌNH BÀY ĐẸP HƠN)
    prompt = PromptTemplate(
        template="""Bạn là Luật sư AI tận tâm và chuyên nghiệp.
        
        Lịch sử trò chuyện:
        {chat_history}
        
        Thông tin pháp lý tìm được:
        {context}
        
        Câu hỏi của khách hàng: {query}
        
        Yêu cầu về định dạng & Phong cách (BẮT BUỘC):
        1. **Mở đầu**: Bắt đầu bằng lời chào thân thiện (Ví dụ: "Chào bạn,", "Chào anh/chị,").
        2. **Bố cục**: Chia câu trả lời thành các đoạn nhỏ, dễ đọc.
           - Sử dụng **Gạch đầu dòng (-)** hoặc **Số thứ tự (1., 2.)** khi liệt kê quy trình, hồ sơ.
           - **In đậm (**từ khóa**)** các ý chính, tên hồ sơ, hoặc bước quan trọng.
        3. **Nội dung**:
           - Trả lời thẳng vào vấn đề.
           - Lồng ghép trích dẫn luật vào câu (VD: "Theo **Điều 51 Luật Hôn nhân...**").
        4. **Cấm**: KHÔNG tự tạo mục "Nguồn tham khảo" ở cuối (Hệ thống đã tự làm).
        5. **Kết thúc**: Lời chúc ngắn gọn, ấm áp (Ví dụ: "Chúc bạn sớm giải quyết được vấn đề!").
        
        Lời tư vấn:""",
        input_variables=["chat_history", "context", "query"]
    )
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        answer = chain.invoke({
            "chat_history": chat_history,
            "context": context_text, 
            "query": query
        })
    except Exception as e:
        answer = "Xin lỗi, tôi gặp sự cố khi soạn thảo câu trả lời."

    return {
        "generation": answer,
        "sources": unique_sources
    }