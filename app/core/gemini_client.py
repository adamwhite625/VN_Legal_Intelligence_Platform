import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# --- CẤU HÌNH ---
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = os.getenv("QDRANT_PORT", "6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "law_data")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

client = QdrantClient(host=QDRANT_HOST, port=int(QDRANT_PORT))

# Dùng model Multilingual (384 dimensions)
print("[THÔNG TIN] Đang tải model Embedding cho Search...")
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={"device": "cpu"}
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3
)

# Prompt xử lý tình huống
prompt_template = ChatPromptTemplate.from_template("""
Bạn là Luật sư AI tư vấn pháp luật Việt Nam chuyên nghiệp.
Nhiệm vụ của bạn là giải quyết tình huống pháp lý dựa trên thông tin được cung cấp.

Quy trình tư vấn:
1. Phân tích tình huống của người dùng.
2. Đối chiếu với các điều luật trong phần "Cơ sở pháp lý".
3. Đưa ra câu trả lời chi tiết, chia các trường hợp có thể xảy ra (nếu có).
4. Luôn trích dẫn cụ thể (Ví dụ: Theo Khoản 2 Điều 81 Luật Hôn nhân Gia đình...).

Lưu ý:
- Nếu thông tin luật không đủ để kết luận, hãy nêu rõ quan điểm dựa trên những gì đang có và khuyên người dùng tham khảo thêm.
- Không được bịa đặt điều luật không có trong "Cơ sở pháp lý".

Cơ sở pháp lý (Context):
{context}

Câu hỏi/Tình huống của người dùng:
{question}

Lời tư vấn của luật sư:
""")

def get_law_answer(user_question: str):
    try:
        # Bước 1: Vector hóa câu hỏi
        query_vector = embeddings_model.embed_query(user_question)

        # Bước 2: Tìm kiếm (DÙNG query_points THAY VÌ search ĐỂ TRÁNH LỖI)
        search_result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector, # Lưu ý: tham số là query, không phải query_vector
            limit=5 
        ).points # Lưu ý: Phải lấy thuộc tính .points

        # Bước 3: Ghép ngữ cảnh
        context_text = ""
        sources = []
        
        if not search_result:
            return {
                "answer": "Xin lỗi, tôi chưa tìm thấy quy định pháp luật liên quan trong cơ sở dữ liệu hiện tại.",
                "sources": []
            }

        for hit in search_result:
            law_content = hit.payload.get("combine_Article_Content", "")
            law_id = hit.payload.get("so_hieu", "")
            law_name = hit.payload.get("loai_van_ban", "")
            
            context_text += f"[{law_id} - {law_name}]: {law_content}\n\n"
            sources.append(f"{law_id} - {law_name}")

        # Bước 4: Gửi cho Gemini
        chain = prompt_template | llm | StrOutputParser()
        answer = chain.invoke({"context": context_text, "question": user_question})

        return {
            "answer": answer,
            "sources": list(set(sources))
        }

    except Exception as e:
        print(f"[LỖI] {e}")
        return {"answer": "Đã xảy ra lỗi hệ thống. Vui lòng kiểm tra log.", "sources": []}