import os
import json
import logging
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.limiter import limiter
from app.core.config import settings
from app.api.v1.api import api_router
from app.api.v1.health import router as health_router
from app.core.clients import init_clients, close_clients
from app.exceptions import setup_exception_handlers

logger = logging.getLogger("app.main")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle for starting and cleaning up resources."""
    logger.info("Application starting up: collection=%s, db_host=%s", settings.COLLECTION_NAME, settings.DB_HOST)
    try:
        init_clients()
        logger.info("All clients initialized successfully")
    except Exception as e:
        logger.error("Error during application startup: %s", str(e))
        raise e

    yield

    close_clients()


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

# Rate limiter setup
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)


@app.middleware("http")
async def request_context(request, call_next):
    """Inject request ID and record HTTP request processing time."""
    request_id = request.headers.get("X-Request-ID", "") or str(uuid4())
    started_at = perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    duration_ms = round((perf_counter() - started_at) * 1000, 3)
    
    log_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
    }
    logger.info(json.dumps(log_payload))
    return response


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://legal-chatbot-alb-1754962006.ap-southeast-1.elb.amazonaws.com",
]

# Allow additional origins from environment variable
extra_origin = os.getenv("CORS_ORIGIN")
if extra_origin:
    origins.append(extra_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_exception_handlers(app)

app.include_router(health_router)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    """Return root welcome message."""
    return {"message": "Legal Chatbot API is Ready"}