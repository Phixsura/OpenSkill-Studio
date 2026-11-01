"""Response cache — HTTP response caching with ETags and conditional requests."""

import hashlib
from datetime import datetime, timedelta


def generate_etag(*, content: str) -> str:
    return f'"{hashlib.md5(content.encode()).hexdigest()}"'


def build_cache_headers(*, content: str, max_age: int = 300,
                          private: bool = False) -> dict:
    etag = generate_etag(content=content)
    cache_control = f"{'private' if private else 'public'}, max-age={max_age}"
    expires = (datetime.utcnow() + timedelta(seconds=max_age)).strftime("%a, %d %b %Y %H:%M:%S GMT")
    return {
        "ETag": etag,
        "Cache-Control": cache_control,
        "Expires": expires,
        "Vary": "Accept-Encoding",
    }


def check_conditional(*, if_none_match: str | None, current_etag: str) -> dict:
    if if_none_match and if_none_match == current_etag:
        return {"status": 304, "message": "Not Modified", "send_body": False}
    return {"status": 200, "message": "OK", "send_body": True}
