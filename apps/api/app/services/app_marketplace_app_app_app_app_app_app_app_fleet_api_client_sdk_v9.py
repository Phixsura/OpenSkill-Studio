"""Fleet API Client SDK v9 — track SDK client library health."""
from __future__ import annotations
def fleet_api_client_sdk_v9(sdks: list[dict]) -> dict:
    up_to_date = [s for s in sdks if s.get("up_to_date")]
    downloads = sum(s.get("weekly_downloads", 0) for s in sdks)
    issues = sum(s.get("open_issues", 0) for s in sdks)
    return {"sdks": len(sdks), "up_to_date": len(up_to_date), "weekly_downloads": downloads,
            "open_issues": issues, "healthy": issues == 0}
