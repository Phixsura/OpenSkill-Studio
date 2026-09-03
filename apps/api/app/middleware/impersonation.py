"""Impersonation read-only guard (ADR-014 §1.5, fail-closed by design).

An impersonated session (access token carrying an `imp` claim) may only
perform GET/HEAD/OPTIONS requests, plus a tiny whitelist of low-risk writes
needed for support debugging. Enforcing this in middleware — rather than
per-endpoint deny dependencies — means a newly added endpoint is protected
by default instead of accidentally open.
"""

import re

import jwt as _jwt
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings
from app.core.security import ALGORITHM

log = structlog.get_logger()

_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})

# Low-risk writes an impersonated support session may perform.
_WRITE_WHITELIST = [
    re.compile(r"^/api/v1/notifications/[^/]+/read$"),
    re.compile(r"^/api/v1/notifications/read-all$"),
]


class ImpersonationGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in _SAFE_METHODS:
            return await call_next(request)
        auth = request.headers.get("authorization", "")
        # Parse the scheme exactly the way FastAPI's OAuth2PasswordBearer does
        # (case-insensitive, single partition on the first space) so this guard
        # sees the bearer token on EVERY request the route will authenticate.
        # A naive `auth.startswith("Bearer ")` was case-sensitive: a lowercase
        # `bearer <imp-token>` (or extra whitespace) slipped past the guard while
        # the route still authenticated it — a full read-only-impersonation
        # bypass. token.strip() keeps us at least as lenient as route auth so we
        # never fail open (over-blocking a request the route would 401 is safe).
        scheme, _, token = auth.partition(" ")
        if scheme.lower() != "bearer":
            return await call_next(request)
        token = token.strip()
        try:
            payload = _jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        except Exception:  # noqa: BLE001 — invalid tokens are the route auth's problem
            return await call_next(request)
        if "imp" not in payload:
            return await call_next(request)
        path = request.url.path
        if any(rx.match(path) for rx in _WRITE_WHITELIST):
            return await call_next(request)
        log.warning(
            "impersonation_write_blocked",
            path=path,
            method=request.method,
            imp_grant=payload.get("imp_grant"),
            request_id=getattr(request.state, "request_id", None),
        )
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "IMPERSONATION_FORBIDDEN",
                    "message": "Impersonated sessions are read-only",
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )
