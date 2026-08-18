import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware

log = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start

        # Attach rate limit headers if set by the rate_limit dependency
        rl_headers = getattr(request.state, "rate_limit_headers", None)
        if rl_headers:
            for k, v in rl_headers.items():
                response.headers[k] = v

        log.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(elapsed * 1000, 2),
            request_id=getattr(request.state, "request_id", None),
        )
        return response
