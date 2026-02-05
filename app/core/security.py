import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

# Import Models và Database để truy vấn user
from app.database import get_db
from app import models

# 1. Load biến môi trường
load_dotenv()

# 2. Cấu hình
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if not SECRET_KEY:
    raise ValueError("⚠️ CHƯA CẤU HÌNH SECRET_KEY TRONG FILE .ENV")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ==========================================
# 1. CÁC HÀM TIỆN ÍCH (HELPER FUNCTIONS)
# ==========================================

def verify_password(plain_password, hashed_password):
    """Kiểm tra mật khẩu nhập vào có khớp với hash không"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Mã hóa mật khẩu"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Tạo JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ==========================================
# 2. CÁC HÀM DEPENDENCY (NGƯỜI GÁC CỔNG)
# ==========================================

# --- Gác cổng 1: Xác thực User (Bất kỳ ai đã login) ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Hàm này sẽ:
    1. Lấy token từ header
    2. Giải mã token để lấy email
    3. Tìm user trong DB
    4. Nếu OK -> Trả về user object (cho API dùng)
    5. Nếu lỗi -> Báo 401 Unauthorized
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Giải mã token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Truy vấn DB tìm user
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user

# --- Gác cổng 2: Xác thực Admin (Chỉ Admin mới qua được) ---
def get_current_admin(current_user: models.User = Depends(get_current_user)):
    """
    Hàm này dựa vào hàm get_current_user ở trên.
    Nó kiểm tra thêm trường 'role' có phải là 'admin' không.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập (Yêu cầu quyền Admin)"
        )
    return current_user