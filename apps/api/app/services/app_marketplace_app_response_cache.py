"""Response cache — intelligent caching with cache-control headers and invalidation."""

import hashlib
import time


def compute_cache_key(*, method: str, path: str, query_params: dict | None = None) -> str:
    parts = f"{method}:{path}"
    if query_params:
        sorted_params = "&".join(f"{k}={v}" for k, v in sorted(query_params.items()))
        parts += f"?{sorted_params}"
    return hashlib.sha256(parts.encode()).hexdigest()[:16]


def build_cache_headers(*, max_age: int = 300, private: bool = False,
                           stale_while_revalidate: int = 60) -> dict:
    directives = []
    directives.append("private" if private else "public")
    directives.append(f"max-age={max_age}")
    if stale_while_revalidate:
        directives.append(f"stale-while-revalidate={stale_while_revalidate}")
    return {"Cache-Control": ", ".join(directives)}


def should_cache(*, method: str, status_code: int, content_type: str) -> bool:
    if method.upper() != "GET":
        return False
    if status_code not in (200, 301, 304):
        return False
    cacheable_types = {"application/json", "text/html", "text/css", "application/javascript"}
    return any(content_type.startswith(t) for t in cacheable_types)


def compute_cache_hit_rate(*, hits: int, misses: int) -> dict:
    total = hits + misses
    rate = round(hits / max(total, 1) * 100, 1)
    return {"hits": hits, "misses": misses, "total": total, "hit_rate": rate,
            "efficiency": "excellent" if rate > 90 else "good" if rate > 70 else "poor"}
