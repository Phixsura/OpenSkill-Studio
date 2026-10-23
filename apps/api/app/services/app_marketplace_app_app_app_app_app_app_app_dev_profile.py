"""Developer profile builder — public developer profiles for the marketplace."""
from __future__ import annotations
import html


def build_developer_profile(dev: dict) -> dict:
    name = html.escape(dev.get("name", ""))
    bio = html.escape(dev.get("bio", "")[:300])
    apps = dev.get("apps", [])
    total_installs = sum(a.get("installs", 0) for a in apps)
    avg_rating = round(sum(a.get("rating", 0) for a in apps) / max(len(apps), 1), 1)
    return {
        "name": name, "bio": bio,
        "avatar": dev.get("avatar", ""),
        "website": dev.get("website", ""),
        "verified": dev.get("verified", False),
        "joined": dev.get("joined", ""),
        "app_count": len(apps),
        "total_installs": total_installs,
        "total_installs_display": f"{total_installs:,}",
        "avg_rating": avg_rating,
        "apps": [{"name": html.escape(a.get("name", "")), "icon": a.get("icon", "📱"),
                  "rating": a.get("rating", 0), "installs": a.get("installs", 0)}
                 for a in apps[:6]],
    }
