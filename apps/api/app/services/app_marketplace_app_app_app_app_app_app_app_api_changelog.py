"""API changelog generator — track breaking changes, deprecations, new endpoints."""
from __future__ import annotations


def generate_changelog(entries: list[dict]) -> dict:
    categorized: dict[str, list[dict]] = {"breaking": [], "deprecated": [], "added": [], "fixed": [], "changed": []}
    for e in entries:
        cat = e.get("type", "changed")
        if cat in categorized:
            categorized[cat].append({
                "endpoint": e.get("endpoint", ""),
                "description": e.get("description", ""),
                "version": e.get("version", ""),
                "date": e.get("date", ""),
            })
    has_breaking = len(categorized["breaking"]) > 0
    total = sum(len(v) for v in categorized.values())
    sections = []
    for cat in ("breaking", "deprecated", "added", "fixed", "changed"):
        if categorized[cat]:
            sections.append({"type": cat, "count": len(categorized[cat]),
                             "entries": categorized[cat]})
    return {
        "total_changes": total, "has_breaking": has_breaking,
        "severity": "major" if has_breaking else "minor" if categorized["added"] else "patch",
        "sections": sections,
    }
