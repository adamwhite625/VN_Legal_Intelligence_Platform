from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.clients import get_llm
from app.services.law_agent.state import LawAgentState

def fallback_node(state: LawAgentState) -> LawAgentState:
    llm = get_llm()
    print("🛡️ [FALLBACK]: Kích hoạt quy trình xử lý thiếu thông tin...")
    
    status = state.check_status or "NO_LAW"
    query = state.standalone_query or state.query
    docs = state.retrieved_docs or []
    has_law_context = state.has_law_context  # Use the flag from contextualize
    law_context = state.law_context  # Use the extracted law context
    
    # Content keywords  
    content_keywords = ["nội dung", "là gì", "định nghĩa", "khái niệm", "quy định", "quy định gì", "có nội dung gì", "bao gồm", "gồm những gì"]
    is_content_question = any(keyword in query.lower() for keyword in content_keywords)
    
    # CASE 1: If law context and content question → Answer using the law context
    if has_law_context and law_context and is_content_question:
        print("📄 [FALLBACK]: Có ngữ cảnh luật + câu hỏi nội dung → Sử dụng Writer...")
        from app.services.law_agent.nodes.writer_agent import answer_node
        return answer_node(state)
    
    # CASE 1: NO_LAW status or empty documents
    if status == "NO_LAW" or not docs:
        if not state.web_search_results:
            from app.services.law_agent.nodes.web_search_agent import web_search_node
            state = web_search_node(state)

        if state.web_search_results:
            web_context = "\n".join(state.web_search_results)
            state.generation = (
                f"Trong cơ sở dữ liệu pháp luật Việt Nam chưa có văn bản phù hợp. "
                f"Tuy nhiên, kết quả tìm kiếm web cho thấy:\n\n{web_context}"
            )
            state.search_source = "web"
            state.sources = ["Web Search"]
            state.node_trace.append("fallback")
            return state

        state.generation = (
            "Xin lỗi, hiện tại cơ sở dữ liệu của tôi chưa có văn bản pháp lý chính xác về vấn đề này. "
            "Để đảm bảo an toàn pháp lý, tôi xin phép không tự suy đoán. Bạn vui lòng tham vấn luật sư trực tiếp."
        )
        state.sources = []
        state.node_trace.append("fallback")
        return state

    # TRƯỜNG HỢP 2: CÓ LUẬT NHƯNG THIẾU THÔNG TIN USER
    if status == "MISSING_INFO":
        context_text = "\n".join([f"- {d.content}" for d in docs])
        
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
        
        state.generation = clarification_msg
        state.sources = list(set([d.law_name for d in docs]))
        state.node_trace.append("fallback")
        return state

    state.generation = "Hệ thống đang gặp sự cố xác định trạng thái."
    state.sources = []
    state.node_trace.append("fallback")
    return state