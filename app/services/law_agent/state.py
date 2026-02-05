from typing import TypedDict, List, Dict, Any, Literal, Optional

class LawAgentState(TypedDict):
    """
    Lưu trữ toàn bộ trạng thái của cuộc hội thoại trong quá trình Agent suy nghĩ.
    """
    # 1. Input đầu vào
    query: str                # Câu hỏi gốc của user
    standalone_query: str     # Câu hỏi đã được làm rõ ngữ cảnh (Rewritten)
    chat_history: str         # Lịch sử chat (định dạng text)

    # 2. Suy luận (Router)
    intent: str               # Ý định (SEARCH_PENAL, SEARCH_CIVIL...)
    search_limit: int         # Số lượng văn bản cần tìm

    # 3. Dữ liệu tìm kiếm (Retriever)
    retrieved_docs: List[Dict] # Danh sách các điều luật tìm được

    # 4. Kiểm tra (Checker)
    # 'SUFFICIENT': Đủ dữ liệu -> Trả lời
    # 'MISSING_INFO': Thiếu thông tin -> Hỏi lại user
    # 'NO_LAW': Không tìm thấy luật -> Fallback
    check_status: Literal['SUFFICIENT', 'MISSING_INFO', 'NO_LAW']
    
    # 5. Kết quả đầu ra (Writer / Fallback)
    generation: str           # Câu trả lời cuối cùng của Bot
    sources: List[str]        # Danh sách nguồn tham khảo (Unique)