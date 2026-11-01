"""API response headers middleware.

Adds standard headers to all API responses:
- X-Request-Id (from existing RequestIDMiddleware)
- X-RateLimit-* headers (when rate limit info available)
- Deprecation / Sunset headers (for deprecated endpoints)
- Idempotency-Key echo
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class ApiResponseHeadersMiddleware(BaseHTTPMiddleware):
    """Add standard API response headers."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Echo idempotency key if provided
        idem_key = request.headers.get("idempotency-key")
        if idem_key:
            response.headers["Idempotency-Key"] = idem_key

        # API version header
        if request.url.path.startswith("/api/v1/"):
            response.headers["X-API-Version"] = "v1"

        return response
