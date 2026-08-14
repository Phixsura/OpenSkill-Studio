import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware

log = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start

        log.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(elapsed * 1000, 2),
            request_id=getattr(request.state, "request_id", None),
        )
        return response
