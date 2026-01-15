import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# 1. Cấu hình Qdrant
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = os.getenv("QDRANT_PORT", "6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "law_data")

# 2. Khởi tạo Client
client = QdrantClient(host=QDRANT_HOST, port=int(QDRANT_PORT))

# 3. Khởi tạo Model Embedding (Dùng model tiếng Việt nhẹ)
# Bạn có thể đổi thành model khác nếu muốn
MODEL_NAME = "keepitreal/vietnamese-bi-encoder" 
print("Loading Embedding Model... (Lần đầu sẽ hơi lâu)")
embeddings_model = HuggingFaceEmbeddings(
    model_name=MODEL_NAME,
    model_kwargs={"device": "cpu"}, # Dùng CPU cho an toàn, nếu có GPU cài CUDA thì đổi thành 'cuda'
    encode_kwargs={"normalize_embeddings": True}
)

def search_relevant_documents(query: str, top_k: int = 5):
    """
    Tìm kiếm văn bản liên quan trong Qdrant
    """
    try:
        # 1. Mã hóa câu hỏi thành vector
        query_vector = embeddings_model.embed_query(query)

        # 2. Tìm kiếm trong Qdrant
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True # Lấy cả nội dung văn bản gốc
        )
        
        return search_result
        
    except Exception as e:
        print(f"Error searching Qdrant: {e}")
        return []

# Hàm test nhanh
if __name__ == "__main__":
    results = search_relevant_documents("Luật doanh nghiệp")
    print(f"Tìm thấy {len(results)} kết quả.")