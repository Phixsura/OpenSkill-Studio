"""Fleet learnings DB — searchable incident knowledge base."""
from __future__ import annotations
def fleet_learnings_db(entries: list[dict]) -> dict:
    by_category: dict[str, int] = {}
    for e in entries:
        cat = e.get("category", "other")
        by_category[cat] = by_category.get(cat, 0) + 1
    return {"total_entries": len(entries), "categories": len(by_category),
            "by_category": by_category, "rich": len(entries) >= 50}
