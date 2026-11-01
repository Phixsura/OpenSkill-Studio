"""Command palette — searchable command registry."""
from __future__ import annotations
import re


def register_commands(commands: list[dict]) -> dict:
    items = []
    for c in commands:
        items.append({"id": c.get("id", ""), "label": c.get("label", ""),
                       "shortcut": c.get("shortcut", ""),
                       "category": c.get("category", "general"),
                       "keywords": c.get("keywords", [])})
    by_cat: dict[str, int] = {}
    for i in items:
        by_cat[i["category"]] = by_cat.get(i["category"], 0) + 1
    return {"commands": items, "total": len(items), "by_category": by_cat}


def search_commands(registry: dict, query: str, limit: int = 10) -> list[dict]:
    if not query:
        return registry["commands"][:limit]
    q = query.lower()
    results = []
    for cmd in registry["commands"]:
        label_match = q in cmd["label"].lower()
        kw_match = any(q in kw.lower() for kw in cmd["keywords"])
        cat_match = q in cmd["category"].lower()
        if label_match or kw_match or cat_match:
            score = 3 if label_match else 2 if kw_match else 1
            results.append({**cmd, "score": score})
    return sorted(results, key=lambda x: -x["score"])[:limit]
