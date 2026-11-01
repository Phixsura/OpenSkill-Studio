"""Fleet SDK Analytics v9 — track SDK usage across languages."""
from __future__ import annotations
def fleet_sdk_analytics_v9(sdks: list[dict]) -> dict:
    languages = len({s.get("language") for s in sdks if s.get("language")})
    downloads = sum(s.get("downloads_today", 0) for s in sdks)
    active_users = sum(s.get("active_users", 0) for s in sdks)
    return {"sdks": len(sdks), "languages": languages, "downloads_today": downloads,
            "active_users": active_users, "healthy": True}
