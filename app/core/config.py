import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient

# ==========================================
# 1. CLASS CẤU HÌNH (SETTINGS)
# ==========================================
class Settings(BaseSettings):
    # --- Thông tin Project ---
    PROJECT_NAME: str = "Legal Chatbot"
    API_V1_STR: str = "/api/v1"

    # --- Database & Vector DB ---
    # Nếu quên set trong .env, nó sẽ dùng giá trị mặc định sau dấu "="
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    COLLECTION_NAME: str = "law_data"
    
    # --- Security (Bắt buộc phải có trong .env, không có default) ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # --- External APIs ---
    GOOGLE_API_KEY: str

    # Cấu hình để đọc file .env
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_ignore_empty=True,
        extra="ignore" # Bỏ qua các biến thừa trong .env
    )

# Khởi tạo đối tượng settings duy nhất dùng chung
settings = Settings()

# ==========================================
# 2. KHỞI TẠO CÁC KẾT NỐI (INSTANCES)
# ==========================================

# --- Qdrant Client ---
client = QdrantClient(
    host=settings.QDRANT_HOST, 
    port=settings.QDRANT_PORT
)

# --- Embeddings Model ---
# Model này tải về local, nên khởi tạo 1 lần dùng chung
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# --- LLM (Gemini) ---
# Dùng settings.GOOGLE_API_KEY thay vì os.getenv
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0
)

# (Tùy chọn) In ra log để biết config đã load
print(f"Loaded Config: Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")