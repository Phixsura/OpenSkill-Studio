"""Fleet API SDK v9 — track SDK generation and distribution."""
from __future__ import annotations
def fleet_api_sdk_v9(sdks: list[dict]) -> dict:
    generated = [s for s in sdks if s.get("generated")]
    published = [s for s in sdks if s.get("published")]
    languages = len({s.get("language") for s in sdks if s.get("language")})
    downloads = sum(s.get("downloads_total", 0) for s in sdks)
    return {"sdks": len(sdks), "generated": len(generated), "published": len(published),
            "languages": languages, "total_downloads": downloads, "healthy": len(published) == len(generated)}
