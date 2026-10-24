"""Deployment changelog generator — auto-generate changelogs for deployments."""
from __future__ import annotations
import html


def generate_deploy_changelog(version: str, commits: list[dict], deployer: str) -> dict:
    by_type: dict[str, list[str]] = {}
    for c in commits:
        ctype = c.get("type", "other")
        by_type.setdefault(ctype, []).append(html.escape(c.get("message", "")))
    sections = []
    type_labels = {"feat": "Features", "fix": "Bug Fixes", "perf": "Performance", "docs": "Docs", "other": "Other"}
    for t, msgs in by_type.items():
        sections.append({"type": t, "label": type_labels.get(t, t.title()), "items": msgs})
    return {"version": version, "deployer": html.escape(deployer), "sections": sections,
            "commit_count": len(commits), "type_count": len(sections)}
