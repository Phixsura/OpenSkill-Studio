"""Changelog generator — auto-generate changelogs from commits."""

import re
from datetime import datetime


COMMIT_TYPES = {
    "feat": "Features", "fix": "Bug Fixes", "perf": "Performance",
    "docs": "Documentation", "refactor": "Refactoring", "chore": "Chores",
}


def parse_commits(*, commits: list[str]) -> dict:
    groups: dict[str, list[str]] = {}
    breaking = []
    for msg in commits:
        m = re.match(r"^(\w+)(?:\(.+?\))?(!)?:\s*(.+)$", msg)
        if m:
            ctype, bang, desc = m.group(1), m.group(2), m.group(3)
            label = COMMIT_TYPES.get(ctype, "Other")
            groups.setdefault(label, []).append(desc)
            if bang:
                breaking.append(desc)
        else:
            groups.setdefault("Other", []).append(msg)
    return {"groups": groups, "breaking_changes": breaking,
            "total": len(commits), "has_breaking": len(breaking) > 0}


def render_changelog(*, version: str, date: str | None = None,
                       parsed: dict) -> str:
    d = date or datetime.utcnow().strftime("%Y-%m-%d")
    lines = [f"## {version} ({d})\n"]
    if parsed["has_breaking"]:
        lines.append("### ⚠️ Breaking Changes\n")
        for b in parsed["breaking_changes"]:
            lines.append(f"- {b}")
        lines.append("")
    for section, items in parsed["groups"].items():
        lines.append(f"### {section}\n")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)
