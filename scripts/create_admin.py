import sys
import os

# Thêm đường dẫn hiện tại vào sys.path
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from app.core import security

# Cấu hình kết nối
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:legalbot_password@localhost:3306/law_chatbot_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ======================================================
# 🔥 THÊM DÒNG NÀY ĐỂ TẠO BẢNG TRƯỚC KHI TẠO ADMIN 🔥
# ======================================================
models.Base.metadata.create_all(bind=engine)
# ======================================================

def create_super_admin():
    db = SessionLocal()
    try:
        print("--- TẠO TÀI KHOẢN ADMIN ---")
        email = input("Nhập Email: ")
        password = input("Nhập Mật khẩu: ")
        full_name = input("Nhập Họ tên: ")

        # 1. Kiểm tra xem email đã có chưa
        user = db.query(models.User).filter(models.User.email == email).first()
        
        if user:
            print(f"⚠️ User {email} đã tồn tại!")
            confirm = input("Bạn có muốn nâng quyền user này lên ADMIN không? (y/n): ")
            if confirm.lower() == 'y':
                user.role = "admin"
                db.commit()
                print(f"✅ Đã nâng cấp {email} thành ADMIN!")
        else:
            # 2. Tạo Admin mới
            hashed_password = security.get_password_hash(password)
            new_admin = models.User(
                email=email,
                hashed_password=hashed_password,
                full_name=full_name,
                role="admin" 
            )
            db.add(new_admin)
            db.commit()
            print(f"✅ Đã tạo thành công Admin: {email}")

    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_super_admin()