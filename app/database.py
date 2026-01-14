from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "legalbot_password")
DB_HOST = os.getenv("DB_SERVER", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "law_chatbot_db")

SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Tạo Engine kết nối
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True, # Tự động kiểm tra kết nối để tránh lỗi ngắt kết nối
    pool_recycle=3600
)

# Tạo SessionLocal để dùng trong các request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho các Models kế thừa
Base = declarative_base()

# Hàm dependency để lấy DB Session (Dùng trong FastAPI route)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()