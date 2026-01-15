from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.database import engine
from app.api import endpoints

# Tạo bảng database (nếu chưa có)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Legal Chatbot API")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Trong production nên đổi thành domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các routes từ endpoints.py
app.include_router(endpoints.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Legal Chatbot System is Ready!"}