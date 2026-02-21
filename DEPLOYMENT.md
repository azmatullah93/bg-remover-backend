# Backend Deployment

Deploy the Background Removal API to Render or Google Cloud Run.

---

## Deploy to Render (recommended)

### Prerequisites

- [Render](https://render.com) account
- Repo pushed to GitHub or GitLab

### Option A: Blueprint (Infrastructure as Code)

1. In [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint**
2. Connect your repo
3. Render will detect `render.yaml` in the repo root
4. **Set `CORS_ORIGINS`** when prompted — your frontend URL (e.g. `https://your-app.vercel.app`)
5. Click **Apply**

### Option B: Manual setup

1. **New** → **Web Service**
2. Connect repo, set **Root Directory** to `backend`
3. Set **Environment** to **Docker**
4. **Advanced** → **Dockerfile Path**: `backend/Dockerfile` (or leave default if root is backend)
5. **Instance Type**: **Standard** (2 GB RAM — required for rembg model; Free/Starter may OOM)
6. Add environment variables:
   - `CORS_ORIGINS` = your frontend URL (required)
   - `MAX_FILE_SIZE_MB` = 8 (optional)
   - `RATE_LIMIT_PER_MINUTE` = 10 (optional)
   - `MODEL_NAME` = u2net (optional; use `u2netp` for lighter model on smaller instances)
7. Deploy

### After deploy

- Service URL: `https://rmbg-backend.onrender.com` (or your custom domain)
- Set `NEXT_PUBLIC_API_URL` in your frontend to this URL
- Health check: `curl https://YOUR_SERVICE.onrender.com/health`

### Render tips

- **Cold starts**: First request may take 30–60s while the model loads. Standard plan keeps instances warmer.
- **Cost**: Standard ($25/mo) recommended; Free/Starter may fail with OOM on first request.
- **Region**: Edit `region` in `render.yaml` (e.g. `frankfurt`, `singapore`) for lower latency.

---

## Deploy to Google Cloud Run

This guide covers deploying to Google Cloud Run using best practices.

## Prerequisites

1. **Google Cloud CLI** – [Install gcloud](https://cloud.google.com/sdk/docs/install)
2. **Project** – Create or select a GCP project

## One-Time Setup

```bash
# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com
```

## Deploy

From the **backend** directory:

```bash
cd backend
gcloud builds submit --config cloudbuild.yaml .
```

This will:

1. Build the Docker image
2. Push to Container Registry (gcr.io)
3. Deploy to Cloud Run with:
   - 2 GiB memory (for rembg model)
   - 2 CPUs
   - 5 min request timeout
   - Scale-to-zero (min 0, max 10 instances)

## Configure CORS

After the first deploy, set your frontend URL for CORS:

```bash
gcloud run services update rmbg-backend \
  --region us-central1 \
  --set-env-vars "CORS_ORIGINS=https://your-frontend-domain.com"
```

For multiple origins:

```bash
gcloud run services update rmbg-backend \
  --region us-central1 \
  --set-env-vars "CORS_ORIGINS=https://app.example.com,https://www.example.com"
```

## Get the Service URL

```bash
gcloud run services describe rmbg-backend --region us-central1 --format 'value(status.url)'
```

Use this URL as `NEXT_PUBLIC_API_URL` in your frontend `.env`.

## Manual Deploy (without Cloud Build)

```bash
# Build and push
docker build -t gcr.io/YOUR_PROJECT_ID/rmbg-backend .
docker push gcr.io/YOUR_PROJECT_ID/rmbg-backend

# Deploy
gcloud run deploy rmbg-backend \
  --image gcr.io/YOUR_PROJECT_ID/rmbg-backend \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CORS_ORIGINS` | Allowed origins (comma-separated) | Set via Cloud Run |
| `MAX_FILE_SIZE_MB` | Max upload size | 8 |
| `RATE_LIMIT_PER_MINUTE` | Rate limit per IP | 10 |
| `MODEL_NAME` | rembg model (u2net, u2netp, etc.) | u2net |

## Health Check

```bash
curl https://YOUR_SERVICE_URL/health
```

## Tips

- **Cold starts**: First request may take 30–60s while the model loads. Use `--min-instances 1` to keep one instance warm (higher cost).
- **Region**: Change `_REGION` in `cloudbuild.yaml` for lower latency (e.g. `europe-west1`).
- **Private access**: Remove `--allow-unauthenticated` and use IAM for auth.
