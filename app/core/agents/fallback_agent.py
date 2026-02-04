from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import llm

def fallback_node(state):
    """
    Node 6: Xử lý thông minh khi thiếu thông tin.
    """
    status = state["check_status"]
    query = state.get("standalone_query", state["query"])
    docs = state["retrieved_docs"]
    
    # TRƯỜNG HỢP A: Không có luật (NO_LAW) -> Từ chối thẳng thừng (Rule cứng)
    if status == "NO_LAW":
        print("🧠 [FALLBACK]: Từ chối vì không có dữ liệu luật.")
        msg = (
            "Xin lỗi, hiện tại cơ sở dữ liệu của tôi chưa có đủ văn bản pháp lý chính xác để trả lời câu hỏi này.\n"
            "Để đảm bảo an toàn pháp lý, tôi xin phép không tự suy đoán. Bạn vui lòng tham vấn luật sư trực tiếp."
        )
        return {"generation": msg, "sources": []}

    # TRƯỜNG HỢP B: Có luật nhưng thiếu thông tin user (MISSING_INFO) -> Hỏi lại (Clarification)
    if status == "MISSING_INFO":
        print("🧠 [FALLBACK]: Đang tạo câu hỏi làm rõ (Clarification)...")
        context = "\n".join([f"- {d['content']}" for d in docs])
        
        prompt = PromptTemplate(
            template="""Bạn là Luật sư tư vấn.
            Bạn đã tìm thấy quy định pháp luật liên quan, nhưng chưa thể áp dụng chính xác vì người hỏi cung cấp thiếu thông tin chi tiết.
            
            Văn bản luật:
            {context}
            
            Câu hỏi người dân: {query}
            
            Nhiệm vụ:
            Hãy viết câu trả lời theo cấu trúc sau:
            1. Khẳng định: "Vấn đề này được quy định tại [Tên luật], tuy nhiên kết quả phụ thuộc vào từng trường hợp cụ thể."
            2. Yêu cầu: "Để tôi tư vấn chính xác, bạn vui lòng cung cấp thêm:"
            3. Liệt kê: Các gạch đầu dòng những thông tin cần thiết (Ví dụ: Độ tuổi, loại hợp đồng, thời điểm ký kết...). Dựa chính xác vào các điều kiện ghi trong văn bản luật ở trên.
            
            Lời tư vấn:
            """,
            input_variables=["context", "query"]
        )
        
        chain = prompt | llm | StrOutputParser()
        msg = chain.invoke({"context": context, "query": query})
        
        # Vẫn trả về nguồn để user tin tưởng là mình có căn cứ
        sources = list(set([d['source'] for d in docs]))
        return {"generation": msg, "sources": sources}
        
    return {"generation": "Lỗi xử lý trạng thái.", "sources": []}