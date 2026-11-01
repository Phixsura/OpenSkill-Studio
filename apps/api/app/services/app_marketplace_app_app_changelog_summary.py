"""Changelog summary — auto-generate release summary from changes."""

import html
from collections import Counter


def summarize_changelog(*, entries: list[dict], version: str) -> dict:
    type_counts = Counter(e.get("type", "other") for e in entries)
    highlights = [html.escape(e.get("title", "")) for e in entries if e.get("highlight")][:3]
    breaking = [html.escape(e.get("title", "")) for e in entries if e.get("type") == "breaking"]
    authors = list(set(e.get("author", "") for e in entries if e.get("author")))
    summary_parts = []
    if type_counts.get("added"):
        summary_parts.append(f"{type_counts['added']} new features")
    if type_counts.get("fixed"):
        summary_parts.append(f"{type_counts['fixed']} bug fixes")
    if type_counts.get("performance"):
        summary_parts.append(f"{type_counts['performance']} performance improvements")
    if breaking:
        summary_parts.append(f"{len(breaking)} breaking changes")
    summary = f"v{version}: " + ", ".join(summary_parts) if summary_parts else f"v{version}: {len(entries)} changes"
    return {"version": version, "summary": summary, "total_changes": len(entries),
            "type_counts": dict(type_counts), "highlights": highlights,
            "breaking_changes": breaking, "has_breaking": len(breaking) > 0,
            "contributors": authors, "contributor_count": len(authors)}
