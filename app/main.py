from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.database import engine
from app.api import endpoints, auth

# Tạo bảng database (nếu chưa có)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Legal Chatbot API")

origins = [
    "http://localhost:5173",    # Frontend React (Vite)
    "http://127.0.0.1:5173",    # Frontend IP local
    "http://localhost:3000",   
]

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Cho phép các nguồn này gọi API
    allow_credentials=True,     # Cho phép gửi cookie/token
    allow_methods=["*"],        # Cho phép mọi method (GET, POST, DELETE...)
    allow_headers=["*"],        # Cho phép mọi header
)

# Đăng ký các routes từ endpoints.py
app.include_router(endpoints.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])

@app.get("/")
def read_root():
    return {"message": "Legal Chatbot System is Ready!"}