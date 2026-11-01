"""Changelog generator — generate changelogs from commits."""
from __future__ import annotations
import html
import re

TYPES = {"feat": "Features", "fix": "Bug Fixes", "perf": "Performance",
         "docs": "Documentation", "refactor": "Refactoring", "chore": "Chores"}
CONV_RE = re.compile(r"^(feat|fix|perf|docs|refactor|chore)(?:\(([^)]+)\))?\s*:\s*(.+)$", re.IGNORECASE)


def parse_commits(messages: list[str]) -> list[dict]:
    parsed = []
    for msg in messages:
        m = CONV_RE.match(msg.strip())
        if m:
            parsed.append({"type": m.group(1).lower(), "scope": m.group(2) or "",
                           "description": html.escape(m.group(3).strip())})
        else:
            parsed.append({"type": "other", "scope": "", "description": html.escape(msg.strip())})
    return parsed


def generate_changelog(version: str, commits: list[dict]) -> dict:
    sections: dict[str, list[str]] = {}
    for c in commits:
        label = TYPES.get(c["type"], "Other")
        sections.setdefault(label, []).append(c["description"])
    lines = [f"## {version}\n"]
    for section, items in sections.items():
        lines.append(f"\n### {section}\n")
        for item in items:
            lines.append(f"- {item}")
    return {"version": version, "sections": sections,
            "markdown": "\n".join(lines), "commit_count": len(commits)}
