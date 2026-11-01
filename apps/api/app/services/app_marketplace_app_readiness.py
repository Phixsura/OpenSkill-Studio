"""Readiness — Kubernetes readiness probe."""
def readiness_check(*, db_ok: bool = True, cache_ok: bool = True) -> dict:
    ready = db_ok and cache_ok
    return {"ready": ready, "checks": {"database": db_ok, "cache": cache_ok}}
