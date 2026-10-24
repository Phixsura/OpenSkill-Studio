"""Runbook library — searchable library of operational runbooks."""
from __future__ import annotations

_runbooks: dict[str, dict] = {}


def add_runbook(slug: str, title: str, category: str, steps: list[str],
                 tags: list[str] | None = None) -> dict:
    _runbooks[slug] = {"slug": slug, "title": title, "category": category,
                        "steps": steps, "step_count": len(steps),
                        "tags": tags or [], "uses": 0}
    return _runbooks[slug]


def search_runbooks(query: str) -> list[dict]:
    q = query.lower()
    return [r for r in _runbooks.values()
            if q in r["title"].lower() or q in r["category"].lower()
            or any(q in t.lower() for t in r["tags"])]


def use_runbook(slug: str) -> dict:
    rb = _runbooks.get(slug)
    if not rb:
        return {"found": False}
    rb["uses"] += 1
    return {"found": True, **rb}


def runbook_stats() -> dict:
    by_cat: dict[str, int] = {}
    for r in _runbooks.values():
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
    return {"total": len(_runbooks), "by_category": by_cat,
            "most_used": max(_runbooks.values(), key=lambda r: r["uses"])["title"] if _runbooks else None}


def clear_runbooks() -> None:
    _runbooks.clear()
