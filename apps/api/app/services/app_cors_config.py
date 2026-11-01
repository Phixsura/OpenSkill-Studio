"""CORS config builder — generate CORS origins for app OAuth flows."""

from urllib.parse import urlparse

def build_cors_origins(redirect_uris: list[str]) -> list[str]:
    """Extract unique origins from redirect URIs for CORS."""
    origins = set()
    for uri in redirect_uris:
        try:
            parsed = urlparse(uri)
            if parsed.scheme and parsed.hostname:
                port = f":{parsed.port}" if parsed.port and parsed.port not in (80, 443) else ""
                origins.add(f"{parsed.scheme}://{parsed.hostname}{port}")
        except Exception:
            continue
    return sorted(origins)


def is_origin_allowed(origin: str, allowed_origins: list[str]) -> bool:
    """Check if an origin is in the allowed list."""
    return origin in allowed_origins
