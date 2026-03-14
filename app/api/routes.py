import asyncio
import logging
import time

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse

from app.core.config import config
from app.core.limiter import limiter
from app.services.bg_removal_service import remove_background_stream
from app.utils.file_utils import InvalidImageError, validate_content_type, validate_image

logger = logging.getLogger("app")
router = APIRouter()
start_time = time.time()


@router.get("/health")
@limiter.exempt
async def health():
    return {"status": "ok"}


@router.get("/status")
@limiter.exempt
async def status():
    uptime_seconds = time.time() - start_time
    return {
        "status": "ok",
        "uptime_seconds": round(uptime_seconds, 2),
        "service": "background-removal",
    }


@router.post("/remove-bg")
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute")
async def remove_bg(
    request: Request,
    image: UploadFile = File(..., description="Image file to remove background from"),
):
    validate_content_type(image.content_type)

    try:
        content = await image.read()
    except Exception as e:
        logger.exception("Failed to read upload: %s", e)
        raise HTTPException(status_code=500, detail="Failed to read uploaded file")

    if len(content) > config.max_upload_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {config.MAX_FILE_SIZE_MB} MB",
        )

    session = request.app.state.rembg_session
    if session is None:
        raise HTTPException(
            status_code=503,
            detail="Background removal service is initializing. Please retry shortly.",
        )

    # Run CPU-intensive sync operation in thread pool to avoid blocking event loop
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, remove_background_stream, content, session
        )
    except InvalidImageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Background removal failed: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Failed to remove background. Please try another image.",
        )

    return StreamingResponse(
        iter([result]),
        media_type="image/png",
        headers={"Content-Disposition": "attachment; filename=removed-bg.png"},
    )
