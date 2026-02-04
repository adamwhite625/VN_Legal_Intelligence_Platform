import os
from typing import TypedDict, List, Dict, Any

# ----------- LangGraph -----------
from langgraph.graph import StateGraph, END

# ----------- LLM & Embeddings --------
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ----------- Qdrant & Search --------------
from qdrant_client import QdrantClient
from duckduckgo_search import DDGS

# ============================================================
# 1. CẤU HÌNH HỆ THỐNG
# ============================================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "law_data" 

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

def print_thought(step_name: str, thought: str, color: str = "\033[94m"):
    reset = "\033[0m"
    print(f"\n{color}🧠 [{step_name}]: {reset}\n{thought}\n{'-'*50}")

# ============================================================
# 2. ĐỊNH NGHĨA STATE (THÊM standalone_query)
# ============================================================

class LawAgentState(TypedDict):
    query: str                # Câu hỏi gốc của người dùng (VD: "Nộp ở đâu")
    standalone_query: str     # Câu hỏi đã hiểu ngữ cảnh (VD: "Nộp hồ sơ ly hôn ở đâu")
    intent: str
    search_strategy: dict
    retrieved_docs: List[Dict] 
    is_sufficient: bool
    generation: str
    sources: List[str]
    chat_history: str         # Lịch sử hội thoại

# ============================================================
# 3. CÁC NODE XỬ LÝ
# ============================================================

# 🟦 NODE 1: Intent Analysis & Contextualization (NÂNG CẤP QUAN TRỌNG)
def intent_analysis_node(state: LawAgentState) -> LawAgentState:
    query = state["query"]
    history = state.get("chat_history", "")
    
    # Bước 1: Viết lại câu hỏi nếu cần (Contextualize)
    if history:
        print_thought("1a. HIỂU NGỮ CẢNH", f"Đang xem xét lịch sử để hiểu câu hỏi: '{query}'")
        rewrite_prompt = PromptTemplate.from_template(
            """Bạn là chuyên gia ngôn ngữ.
            Nhiệm vụ: Viết lại câu hỏi mới nhất của người dùng thành một câu đầy đủ ý nghĩa, dựa trên lịch sử trò chuyện.
            
            Lịch sử trò chuyện:
            {history}
            
            Câu hỏi mới: {query}
            
            Yêu cầu:
            - Nếu câu hỏi mới thiếu chủ ngữ/vị ngữ (ví dụ: "Còn tiền án phí?", "Nộp ở đâu?"), hãy ghép với ý của câu trước để thành câu hoàn chỉnh.
            - Nếu câu hỏi đã đầy đủ, giữ nguyên.
            - CHỈ trả về câu hỏi đã viết lại.
            """
        )
        standalone_query = (rewrite_prompt | llm | StrOutputParser()).invoke({"history": history, "query": query}).strip()
        print_thought("1b. CÂU HỎI ĐÃ HIỂU", f"Gốc: '{query}'\nHiểu là: '{standalone_query}'", "\033[96m")
    else:
        standalone_query = query
        print_thought("1b. CÂU HỎI", f"'{standalone_query}' (Không có lịch sử)", "\033[96m")

    # Bước 2: Phân tích Intent dựa trên câu đã viết lại
    prompt = PromptTemplate.from_template(
        "Phân loại câu hỏi sau: HỎI_MỨC_PHẠT, HỎI_THỦ_TỤC, QUYỀN_NGHĨA_VỤ, ĐỊNH_NGHĨA, KHÔNG_RÕ.\nCâu hỏi: {q}\nChỉ trả về tên nhóm."
    )
    intent = (prompt | llm | StrOutputParser()).invoke({"q": standalone_query}).strip()
    
    # Strategy
    strategy = {"limit": 3}
    if intent == "HỎI_THỦ_TỤC": strategy = {"limit": 5}
    elif intent == "KHÔNG_RÕ": strategy = {"limit": 0}
    
    state["standalone_query"] = standalone_query # Lưu câu hỏi mới vào state
    state["intent"] = intent
    state["search_strategy"] = strategy
    
    print_thought("1c. PHÂN TÍCH Ý ĐỊNH", f"Intent: {intent}", "\033[94m")
    return state

# 🟦 NODE 2: Law Retriever (Sửa để dùng standalone_query)
def law_retriever_node(state: LawAgentState) -> LawAgentState:
    # QUAN TRỌNG: Tìm kiếm bằng câu hỏi ĐÃ HIỂU NGỮ CẢNH, không dùng câu gốc
    query_to_search = state["standalone_query"] 
    limit = state["search_strategy"].get("limit", 3)
    
    if limit == 0:
        state["retrieved_docs"] = []
        return state

    try:
        vector = embeddings.embed_query(query_to_search)
        try:
            results = client.search(collection_name=COLLECTION_NAME, query_vector=vector, limit=limit)
        except AttributeError:
            results = client.query_points(collection_name=COLLECTION_NAME, query=vector, limit=limit).points
            
        docs = []
        log_titles = []
        for r in results:
            payload = r.payload or {}
            source_title = f"{payload.get('law_name', 'Luật')} {payload.get('law_id', '')}".strip()
            
            docs.append({
                "source": source_title,
                "content": payload.get("content", "")
            })
            log_titles.append(f"- {source_title}")
            
        state["retrieved_docs"] = docs
        print_thought("2. TÌM KIẾM VECTOR DB", f"Query: {query_to_search}\nKết quả:\n" + "\n".join(log_titles), "\033[92m")
        
    except Exception as e:
        print(f"⚠️ Lỗi Qdrant: {e}")
        state["retrieved_docs"] = []
        
    return state

# 🟦 NODE 3: Sufficiency Checker
def sufficiency_checker_node(state: LawAgentState) -> LawAgentState:
    docs = state["retrieved_docs"]
    if not docs:
        state["is_sufficient"] = False
        return state

    context_text = "\n".join([f"{d['source']}: {d['content']}" for d in docs])
    prompt = PromptTemplate.from_template(
        "Câu hỏi: {query}\nTài liệu: {context}\nTài liệu có đủ để trả lời không? Trả về CÓ hoặc KHÔNG."
    )
    # Check dựa trên câu hỏi đã hiểu ngữ cảnh
    resp = (prompt | llm | StrOutputParser()).invoke({"query": state["standalone_query"], "context": context_text})
    
    is_sufficient = "CÓ" in resp.upper()
    print_thought("3. KIỂM TRA CĂN CỨ", f"Đủ căn cứ? {is_sufficient}", "\033[93m")
    state["is_sufficient"] = is_sufficient
    return state

# 🟦 NODE 4: Web Search (Fallback)
def web_search_node(state: LawAgentState) -> LawAgentState:
    query = state["standalone_query"] # Search web cũng bằng câu đầy đủ
    print_thought("4. WEB SEARCH", f"Đang tìm Google: {query}...", "\033[96m")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            web_docs = []
            for r in results:
                web_docs.append({
                    "source": "Internet",
                    "content": r.get('body', '')
                })
            state["retrieved_docs"] = web_docs
            state["is_sufficient"] = True
    except:
        state["retrieved_docs"] = []
    return state

# 🟦 NODE 5: Answer Generator
def answer_generator_node(state: LawAgentState) -> LawAgentState:
    docs = state["retrieved_docs"]
    # Dùng câu hỏi gốc trong prompt trả lời để tạo cảm giác tự nhiên, 
    # nhưng dùng ngữ cảnh lịch sử để AI hiểu.
    query = state["query"] 
    history = state.get("chat_history", "")
    
    unique_sources = list(set([d["source"] for d in docs]))
    state["sources"] = unique_sources
    
    context = "\n\n".join([f"Nguồn: {d['source']}\nNội dung: {d['content']}" for d in docs])
    
    prompt = PromptTemplate.from_template(
        """Bạn là Luật sư AI.
        
        Lịch sử trò chuyện:
        {history}
        
        Thông tin pháp lý tìm được (Dựa trên câu hỏi đã hiểu ý):
        {context}
        
        Câu hỏi hiện tại của người dùng: {query}
        
        Yêu cầu: Trả lời tự nhiên, tiếp nối mạch chuyện. Trích dẫn luật rõ ràng."""
    )
    answer = (prompt | llm | StrOutputParser()).invoke({
        "history": history, 
        "context": context, 
        "query": query
    })
    
    print_thought("5. TỔNG HỢP TRẢ LỜI", "Đã xong.", "\033[95m")
    state["generation"] = answer
    return state

# 🟦 NODE 6: Clarification
def clarification_agent_node(state: LawAgentState) -> LawAgentState:
    state["generation"] = "Xin lỗi, tôi chưa tìm thấy đủ căn cứ pháp lý để trả lời câu hỏi này."
    state["sources"] = []
    return state

# ============================================================
# 4. XÂY DỰNG GRAPH
# ============================================================

def route_decision(state: LawAgentState):
    if state["is_sufficient"]: return "generate"
    return "web_search"

workflow = StateGraph(LawAgentState)
workflow.add_node("analyze", intent_analysis_node)
workflow.add_node("retrieve", law_retriever_node)
workflow.add_node("check", sufficiency_checker_node)
workflow.add_node("web_search", web_search_node)
workflow.add_node("generate", answer_generator_node)
workflow.add_node("clarify", clarification_agent_node)

workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "retrieve")
workflow.add_edge("retrieve", "check")

workflow.add_conditional_edges(
    "check",
    route_decision,
    {
        "generate": "generate",
        "web_search": "web_search"
    }
)
workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", END)
workflow.add_edge("clarify", END)

app = workflow.compile()