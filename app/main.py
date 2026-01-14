from fastapi import FastAPI
from app import models
from app.database import engine

# Dòng lệnh này sẽ tự động tạo các bảng trong MySQL nếu chưa tồn tại
# Nó tương đương với việc chạy script CREATE TABLE trong SQL
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Legal Chatbot API is running and DB is connected!"}