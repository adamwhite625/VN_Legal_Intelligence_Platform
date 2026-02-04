import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient

# Load biến môi trường từ .env
load_dotenv()

# ==========================================
# 1. CẤU HÌNH VECTOR DB (QDRANT)
# ==========================================
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "law_data"  # Tên bảng dữ liệu luật

# Khởi tạo Client dùng chung cho toàn bộ app
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# ==========================================
# 2. CẤU HÌNH EMBEDDING (TEXT TO VECTOR)
# ==========================================
# Bắt buộc dùng model này để khớp với dữ liệu 384 chiều đã nạp
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# ==========================================
# 3. CẤU HÌNH LLM (GEMINI)
# ==========================================
# Temperature = 0 để đảm bảo luật sư AI không "sáng tác" lung tung
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)