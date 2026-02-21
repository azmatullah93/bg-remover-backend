import logging
import time
from typing import Callable

from fastapi import Request, Response

logger = logging.getLogger("app")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


async def log_requests(request: Request, call_next: Callable) -> Response:
    start = time.perf_counter()
    method = request.method
    path = request.url.path
    client = request.client.host if request.client else "unknown"
    logger.info("request_start | method=%s path=%s client=%s", method, path, client)

    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "request_end | method=%s path=%s status=%s duration_ms=%.2f",
        method,
        path,
        response.status_code,
        duration_ms,
    )
    return response
