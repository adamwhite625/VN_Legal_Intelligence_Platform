from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.clients import init_clients, close_clients
from app.exceptions import setup_exception_handlers

from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.
    Initialize and cleanup shared resources.
    """
    # Startup
    init_clients()

    yield

    # Shutdown
    close_clients()


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

# --- RATE LIMITER CONFIG ---
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)
# --------------------------

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup custom exception handlers
setup_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {"message": "Legal Chatbot API is Ready (Secured)"}