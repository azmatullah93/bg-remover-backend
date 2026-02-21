# Background Removal API

FastAPI service for AI-powered background removal using rembg.

## Setup

```bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # Unix
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload
```

## Endpoints

- `GET /api/health` - Health check
- `POST /api/remove-bg` - Upload image, receive PNG with background removed

## Environment

| Variable | Description | Default |
|----------|-------------|---------|
| MAX_UPLOAD_SIZE_MB | Max file size in MB | 10 |
| ALLOWED_ORIGINS | CORS origins (comma-separated) | http://localhost:3000 |
| MODEL_NAME | rembg model (u2net, u2netp, etc.) | u2net |
