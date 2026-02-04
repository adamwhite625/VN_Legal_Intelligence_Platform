from typing import TypedDict, List, Dict, Any, Literal

class LawAgentState(TypedDict):
    query: str
    standalone_query: str
    intent: str
    retrieved_docs: List[Dict]
    
    # Trạng thái kiểm tra: 
    # 'SUFFICIENT' (Đủ) | 'MISSING_INFO' (Thiếu thông tin user) | 'NO_LAW' (Không tìm thấy luật)
    check_status: Literal['SUFFICIENT', 'MISSING_INFO', 'NO_LAW'] 
    
    generation: str
    sources: List[str]
    chat_history: str