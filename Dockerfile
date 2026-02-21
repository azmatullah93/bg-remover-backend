# syntax=docker/dockerfile:1
# Backend: FastAPI + rembg for Google Cloud Run
# Best practices: multi-stage, non-root, minimal image

FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# Install build deps (rembg/numpy need compilation on some platforms)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---
FROM python:3.11-slim-bookworm AS runtime

# Security: run as non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy pip packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Ensure scripts in .local are in PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code
COPY --chown=appuser:appuser app/ ./app/

USER appuser

# Cloud Run sets PORT (default 8080); unbuffered for streaming logs
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
EXPOSE 8080

# exec replaces shell so uvicorn receives signals (graceful shutdown)
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
