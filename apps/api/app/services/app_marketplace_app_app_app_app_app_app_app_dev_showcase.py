"""Developer showcase — highlight top developers and their contributions."""
from __future__ import annotations
import html


def build_showcase(developers: list[dict], *, limit: int = 12) -> dict:
    ranked = sorted(developers, key=lambda d: -(d.get("total_installs", 0) + d.get("app_count", 0) * 100))[:limit]
    spotlights = [d for d in ranked if d.get("spotlight", False)]
    items = []
    for d in ranked:
        items.append({
            "name": html.escape(d.get("name", "")),
            "avatar": d.get("avatar", ""),
            "bio": html.escape(d.get("bio", "")[:100]),
            "app_count": d.get("app_count", 0),
            "total_installs": d.get("total_installs", 0),
            "installs_display": f"{d.get('total_installs', 0):,}",
            "verified": d.get("verified", False),
            "spotlight": d.get("spotlight", False),
        })
    return {"developers": items, "total": len(items), "spotlights": len(spotlights)}
