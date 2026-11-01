"""Response cache — HTTP response caching with Cache-Control headers."""

import hashlib
import html
from datetime import datetime, timezone


def build_cache_headers(*, max_age_s: int = 3600, public: bool = True,
                          stale_while_revalidate_s: int = 0,
                          no_cache: bool = False, no_store: bool = False) -> dict:
    directives = []
    if no_store:
        directives.append("no-store")
    elif no_cache:
        directives.append("no-cache")
    else:
        directives.append("public" if public else "private")
        directives.append(f"max-age={max_age_s}")
        if stale_while_revalidate_s > 0:
            directives.append(f"stale-while-revalidate={stale_while_revalidate_s}")
    header = ", ".join(directives)
    return {"Cache-Control": header, "directives": directives, "cacheable": not no_store}


def generate_etag(*, content: str) -> dict:
    h = hashlib.sha256(content.encode()).hexdigest()[:16]
    weak = f'W/"{h}"'
    strong = f'"{h}"'
    return {"etag_weak": weak, "etag_strong": strong, "hash": h}


def check_conditional(*, etag: str, if_none_match: str | None = None) -> dict:
    if if_none_match and etag.strip('"').strip("W/").strip('"') == if_none_match.strip('"').strip("W/").strip('"'):
        return {"status": 304, "cache_hit": True, "message": "Not Modified"}
    return {"status": 200, "cache_hit": False, "message": "OK"}
