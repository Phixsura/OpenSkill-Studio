"""Release notes builder — compile PR-based release notes from changes."""
from __future__ import annotations
import html


def compile_release_notes(*, version: str, date: str, prs: list[dict]) -> dict:
    sections: dict[str, list[dict]] = {}
    contributors: set[str] = set()
    for pr in prs:
        pr_type = pr.get("type", "changed")
        sections.setdefault(pr_type, []).append({
            "title": html.escape(pr.get("title", "")),
            "number": pr.get("number", 0),
            "author": pr.get("author", ""),
        })
        if pr.get("author"):
            contributors.add(pr["author"])
    type_order = ["breaking", "added", "fixed", "changed", "deprecated", "removed"]
    ordered = [{"type": t, "items": sections[t], "count": len(sections[t])}
               for t in type_order if t in sections]
    has_breaking = "breaking" in sections
    return {
        "version": version, "date": date,
        "sections": ordered, "total_prs": len(prs),
        "contributors": sorted(contributors),
        "contributor_count": len(contributors),
        "has_breaking": has_breaking,
    }
