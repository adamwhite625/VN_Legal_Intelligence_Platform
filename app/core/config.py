import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient

# --- THAY ĐỔI: IMPORT OPENAI ---
from langchain_openai import ChatOpenAI 
# -------------------------------

# ==========================================
# 1. CLASS CẤU HÌNH (SETTINGS)
# ==========================================
class Settings(BaseSettings):
    PROJECT_NAME: str = "Legal Chatbot"
    API_V1_STR: str = "/api/v1"

    # --- Database MySQL ---
    DB_USER: str = "root"
    DB_PASSWORD: str = "legalbot_password"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "law_chatbot_db"

    # --- Vector DB ---
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    COLLECTION_NAME: str = "law_data"
    
    # --- Security ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # --- External APIs ---
    # GOOGLE_API_KEY: str  <-- Bỏ cái này
    OPENAI_API_KEY: str  # <-- Thêm cái này

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_ignore_empty=True,
        extra="ignore"
    )

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()

# ==========================================
# 2. KHỞI TẠO CÁC KẾT NỐI
# ==========================================

# --- Qdrant Client ---
client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

# --- Embeddings Model (GIỮ NGUYÊN - KHÔNG ĐƯỢC ĐỔI) ---
# Nếu đổi cái này, bạn bắt buộc phải xóa DB làm lại từ đầu.
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# --- LLM (CHUYỂN SANG OPENAI) ---
# Khuyên dùng "gpt-4o-mini": Rẻ bằng 1/10 gpt-4, thông minh hơn gpt-3.5
llm = ChatOpenAI(
    model="gpt-4o-mini", 
    api_key=settings.OPENAI_API_KEY,
    temperature=0
)

print(f" Config: OpenAI (gpt-4o-mini) & Qdrant at {settings.QDRANT_HOST}")