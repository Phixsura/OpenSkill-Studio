"""Platform changelog aggregator — aggregate changes across all platform services."""
from __future__ import annotations
import html


def aggregate_changelog(services: list[dict]) -> dict:
    all_entries = []
    by_service: dict[str, int] = {}
    for svc in services:
        name = svc.get("name", "unknown")
        entries = svc.get("entries", [])
        by_service[name] = len(entries)
        for e in entries:
            all_entries.append({
                "service": name, "type": e.get("type", "changed"),
                "title": html.escape(e.get("title", "")),
                "date": e.get("date", ""), "version": e.get("version", ""),
            })
    all_entries.sort(key=lambda x: x["date"], reverse=True)
    by_type: dict[str, int] = {}
    for e in all_entries:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1
    return {"entries": all_entries, "total": len(all_entries),
            "by_service": by_service, "by_type": by_type,
            "services_count": len(services)}
