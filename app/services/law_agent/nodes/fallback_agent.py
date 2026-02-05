from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import llm

def fallback_node(state):
    print("🛡️ [FALLBACK]: Kích hoạt quy trình xử lý thiếu thông tin...")
    
    status = state.get("check_status", "NO_LAW")
    query = state.get("standalone_query", state["query"])
    docs = state.get("retrieved_docs", [])
    
    # TRƯỜNG HỢP 1: KHÔNG TÌM THẤY LUẬT
    if status == "NO_LAW" or not docs:
        msg = (
            "Xin lỗi, hiện tại cơ sở dữ liệu của tôi chưa có văn bản pháp lý chính xác về vấn đề này. "
            "Để đảm bảo an toàn pháp lý, tôi xin phép không tự suy đoán. Bạn vui lòng tham vấn luật sư trực tiếp."
        )
        return {"generation": msg, "sources": []}

    # TRƯỜNG HỢP 2: CÓ LUẬT NHƯNG THIẾU THÔNG TIN USER
    if status == "MISSING_INFO":
        context_text = "\n".join([f"- {d['content']}" for d in docs])
        
        prompt = PromptTemplate(
            template="""Bạn là Luật sư tư vấn.
            Bạn đã tìm thấy luật liên quan nhưng chưa thể áp dụng vì khách hàng cung cấp thiếu thông tin.
            
            Luật liên quan:
            {context}
            
            Câu hỏi: {query}
            
            Nhiệm vụ:
            1. Khẳng định vấn đề này có quy định pháp luật.
            2. Hỏi lại khách hàng các thông tin cần thiết để tư vấn chính xác hơn.
            
            Phản hồi:""",
            input_variables=["context", "query"]
        )
        
        chain = prompt | llm | StrOutputParser()
        clarification_msg = chain.invoke({"context": context_text, "query": query})
        
        unique_sources = list(set([d["source"] for d in docs]))
        
        return {
            "generation": clarification_msg,
            "sources": unique_sources
        }

    return {
        "generation": "Hệ thống đang gặp sự cố xác định trạng thái.",
        "sources": []
    }