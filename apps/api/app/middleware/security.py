from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

MAX_BODY_SIZE = 50 * 1024 * 1024  # 50 MB


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Request body size limiting (DoS protection)
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_BODY_SIZE:
            return Response("Request body too large", status_code=413)

        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        # X-XSS-Protection set to 0 — the auditor is deprecated and can itself
        # introduce vulnerabilities. CSP is the correct replacement.
        response.headers["X-XSS-Protection"] = "0"
        # Content-Security-Policy: restrict script/style sources
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        return response
