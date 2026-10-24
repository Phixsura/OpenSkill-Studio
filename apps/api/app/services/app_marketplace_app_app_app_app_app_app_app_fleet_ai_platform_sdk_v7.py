"""Fleet AI SDK v7 — track AI platform SDK ecosystem."""
from __future__ import annotations
def fleet_ai_sdk_v7(sdks: list[dict]) -> dict:
    active = [s for s in sdks if s.get("active", True)]
    languages = set()
    for s in sdks:
        languages.update(s.get("languages", []))
    downloads = sum(s.get("downloads_30d", 0) for s in sdks)
    stars = sum(s.get("stars", 0) for s in sdks)
    return {"sdks": len(sdks), "active": len(active), "languages": len(languages),
            "downloads": downloads, "stars": stars, "popular": stars > 10000}
