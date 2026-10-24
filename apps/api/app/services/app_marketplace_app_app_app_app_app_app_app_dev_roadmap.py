"""Developer roadmap — public product roadmap with voting."""
from __future__ import annotations
import html

STATUSES = ["planned", "in_progress", "completed", "shipped"]


def build_roadmap(items: list[dict]) -> dict:
    columns: dict[str, list[dict]] = {s: [] for s in STATUSES}
    for item in items:
        status = item.get("status", "planned")
        if status in columns:
            columns[status].append({
                "id": item.get("id", ""),
                "title": html.escape(item.get("title", "")),
                "description": html.escape(item.get("description", "")[:200]),
                "votes": item.get("votes", 0),
                "quarter": item.get("quarter", ""),
                "tags": item.get("tags", []),
            })
    for col in columns.values():
        col.sort(key=lambda x: -x["votes"])
    return {"columns": columns, "total_items": len(items),
            "statuses": STATUSES}


def vote_item(items: list[dict], item_id: str) -> dict:
    for item in items:
        if item.get("id") == item_id:
            item["votes"] = item.get("votes", 0) + 1
            return {"id": item_id, "votes": item["votes"]}
    return {"error": "Item not found"}
