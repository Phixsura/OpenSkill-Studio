from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

MAX_BODY_SIZE = 50 * 1024 * 1024  # 50 MB


class BodySizeLimitMiddleware:
    """ASGI middleware that enforces body size limits on ALL requests,
    including chunked transfer encoding (no Content-Length header).

    Works at the ASGI layer by wrapping the `receive` callable to track
    cumulative bytes. Aborts with 413 as soon as the limit is exceeded,
    before the full body is buffered in memory.
    """

    def __init__(self, app: ASGIApp, max_body_size: int = MAX_BODY_SIZE):
        self.app = app
        self.max_body_size = max_body_size

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Quick check: if Content-Length is present and exceeds limit, reject early
        headers = dict(scope.get("headers", []))
        cl = headers.get(b"content-length")
        if cl is not None:
            try:
                if int(cl) > self.max_body_size:
                    response = Response("Request body too large", status_code=413)
                    await response(scope, receive, send)
                    return
            except ValueError:
                response = Response("Invalid Content-Length header", status_code=400)
                await response(scope, receive, send)
                return

        # Wrap receive to enforce streaming body size limit
        total_bytes = 0
        body_exceeded = False

        async def limited_receive() -> dict:
            nonlocal total_bytes, body_exceeded
            message = await receive()
            if message.get("type") == "http.request":
                body = message.get("body", b"")
                total_bytes += len(body)
                if total_bytes > self.max_body_size:
                    body_exceeded = True
                    raise BodyTooLargeError()
            return message

        try:
            await self.app(scope, limited_receive, send)
        except BodyTooLargeError:
            response = Response("Request body too large", status_code=413)
            await response(scope, receive, send)


class BodyTooLargeError(Exception):
    """Raised when streaming body exceeds the configured limit."""


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-XSS-Protection"] = "0"

        # Only apply CSP to HTML responses — JSON API responses don't need it,
        # and applying it breaks Swagger docs in debug mode.
        content_type = response.headers.get("content-type", "")
        if "text/html" in content_type:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        return response
