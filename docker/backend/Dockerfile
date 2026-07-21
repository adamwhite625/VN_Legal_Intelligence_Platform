# --- Stage 1: Builder - Install and compile dependencies ---
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools (only needed for compilation, discarded in final image)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment for clean dependency isolation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Runtime - Lean production image ---
FROM python:3.11-slim

WORKDIR /app

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy backend source code
COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FASTEMBED_CACHE_PATH=/app/model_cache

# Pre-download embedding model into the image for fast startup
RUN python scripts/download_models.py

EXPOSE 8080

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
