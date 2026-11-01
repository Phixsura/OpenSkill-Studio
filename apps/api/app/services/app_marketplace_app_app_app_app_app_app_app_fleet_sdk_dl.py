"""Fleet SDK downloads — track SDK download stats by language."""
from __future__ import annotations
def fleet_sdk_downloads(sdks: list[dict]) -> dict:
    total = sum(s.get("downloads", 0) for s in sdks)
    top = max(sdks, key=lambda s: s.get("downloads", 0)) if sdks else None
    return {"total_downloads": total, "sdks": len(sdks),
            "top_sdk": top.get("language") if top else None,
            "top_downloads": top.get("downloads", 0) if top else 0}
