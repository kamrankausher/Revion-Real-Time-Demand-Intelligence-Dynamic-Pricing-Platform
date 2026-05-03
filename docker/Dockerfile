# Multi-stage Dockerfile for ⚡ Revion
# Stage 1: Build dependencies
FROM python:3.10-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production image
FROM python:3.10-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 curl && rm -rf /var/lib/apt/lists/*

# Copy installed packages
COPY --from=builder /install /usr/local

# Copy source code
COPY src/ src/
COPY setup.py .
COPY requirements.txt .

# Create data directories
RUN mkdir -p data/raw data/processed data/features models notebooks

# Install project in dev mode
RUN pip install --no-cache-dir -e .

# Expose ports: FastAPI (8000) + Streamlit (8501)
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
    CMD curl -f http://localhost:8000/health || exit 1

# Default: run API server
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
