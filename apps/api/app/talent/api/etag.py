"""ETag support for talent API GET endpoints (Phase 4C).

Computes weak ETags from response bodies and handles conditional
requests via If-None-Match → 304 Not Modified.

Uses a custom APIRoute subclass so ETags are computed per-route without
the streaming issues of BaseHTTPMiddleware.
"""

from __future__ import annotations

import hashlib

from fastapi import Response
from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse


def compute_etag(body: bytes) -> str:
    """Compute a weak ETag from response body bytes."""
    return f'W/"{hashlib.md5(body, usedforsecurity=False).hexdigest()}"'  # noqa: S324


class ETagRoute(APIRoute):
    """Custom route class that adds ETag headers to GET 200 responses.

    Usage::

        router = APIRouter(route_class=ETagRoute)

    Or apply selectively::

        router.route_class = ETagRoute
    """

    def get_route_handler(self):  # type: ignore[override]
        original_handler = super().get_route_handler()

        async def etag_handler(request: Request) -> StarletteResponse:
            response = await original_handler(request)

            # Only add ETags to successful GET responses
            if request.method != "GET" or response.status_code != 200:
                return response

            body = response.body
            etag = compute_etag(body)
            response.headers["ETag"] = etag

            # Check If-None-Match
            if_none_match = request.headers.get("if-none-match", "")
            if if_none_match == etag:
                return Response(status_code=304, headers={"ETag": etag})

            return response

        return etag_handler
