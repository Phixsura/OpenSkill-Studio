"""Skeleton loader config — define loading skeleton shapes for platform pages."""
from __future__ import annotations

SKELETONS = {
    "dashboard": [
        {"type": "row", "items": [{"w": "25%", "h": "80px"}] * 4},
        {"type": "chart", "w": "100%", "h": "300px"},
        {"type": "table", "rows": 5, "cols": 4},
    ],
    "app_detail": [
        {"type": "header", "w": "60%", "h": "32px"},
        {"type": "row", "items": [{"w": "50%", "h": "200px"}, {"w": "50%", "h": "200px"}]},
        {"type": "table", "rows": 8, "cols": 3},
    ],
    "settings": [
        {"type": "header", "w": "40%", "h": "24px"},
        {"type": "form", "fields": 6, "h": "40px"},
    ],
}


def get_skeleton(page: str) -> dict:
    blocks = SKELETONS.get(page)
    if not blocks:
        return {"page": page, "blocks": [{"type": "header", "w": "50%", "h": "24px"},
                                           {"type": "table", "rows": 5, "cols": 3}]}
    return {"page": page, "blocks": blocks}


def list_pages() -> list[str]:
    return sorted(SKELETONS.keys())
