import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Khởi tạo Model Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3, # Độ sáng tạo thấp để câu trả lời chính xác hơn
    max_output_tokens=2048
)

def generate_answer(query: str, context: str):
    """
    Sinh câu trả lời dựa trên ngữ cảnh (RAG)
    """
    if not context:
        return "Xin lỗi, tôi không tìm thấy văn bản luật nào liên quan đến câu hỏi của bạn trong cơ sở dữ liệu."

    # Prompt Template chuyên nghiệp cho luật sư AI
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """
        Bạn là một Trợ lý Luật sư AI chuyên nghiệp của Việt Nam.
        Nhiệm vụ: Trả lời câu hỏi pháp lý dựa trên thông tin được cung cấp dưới đây.
        
        YÊU CẦU BẮT BUỘC:
        1. Chỉ sử dụng thông tin trong phần "NGỮ CẢNH CUNG CẤP" để trả lời.
        2. Trích dẫn rõ Điều, Khoản, Luật nào (nếu có trong ngữ cảnh).
        3. Giọng văn trang trọng, khách quan, dễ hiểu.
        4. Nếu thông tin không đủ để trả lời, hãy nói: "Dựa trên tài liệu hiện có, tôi chưa thể trả lời chi tiết câu hỏi này."
        
        NGỮ CẢNH CUNG CẤP:
        {context}
        """),
        ("human", "{question}")
    ])

    chain = prompt_template | llm | StrOutputParser()
    
    try:
        response = chain.invoke({"context": context, "question": query})
        return response
    except Exception as e:
        return f"Lỗi khi gọi Gemini: {str(e)}"