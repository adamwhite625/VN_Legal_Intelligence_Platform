from fastapi import APIRouter
from app.api.v1 import auth, chat, admin, search, tracking

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(tracking.router, prefix="/tracking", tags=["Tracking"])