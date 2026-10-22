"""Changelog generator — auto-generate changelog from version diffs."""

from datetime import datetime, timezone


def generate_changelog_entry(*, version: str, changes: list[dict], released_at: str | None = None) -> dict:
    categorized = {"added": [], "changed": [], "fixed": [], "removed": []}
    for c in changes:
        cat = c.get("type", "changed")
        if cat in categorized:
            categorized[cat].append(c.get("description", ""))
    return {
        "version": version, "released_at": released_at or datetime.now(timezone.utc).isoformat(),
        "categories": {k: v for k, v in categorized.items() if v},
        "total_changes": len(changes),
    }


def render_changelog_markdown(*, entries: list[dict]) -> str:
    lines = ["# Changelog\n"]
    for entry in entries:
        lines.append(f"## {entry['version']} ({entry['released_at'][:10]})\n")
        for cat, items in entry.get("categories", {}).items():
            lines.append(f"### {cat.title()}\n")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")
    return "\n".join(lines)


def compare_versions_for_changelog(*, old_manifest: dict, new_manifest: dict) -> list[dict]:
    changes = []
    old_perms = set(old_manifest.get("permissions", []))
    new_perms = set(new_manifest.get("permissions", []))
    for p in new_perms - old_perms:
        changes.append({"type": "added", "description": f"Permission: {p}"})
    for p in old_perms - new_perms:
        changes.append({"type": "removed", "description": f"Permission: {p}"})
    if old_manifest.get("entry_point") != new_manifest.get("entry_point"):
        changes.append({"type": "changed", "description": "Entry point updated"})
    return changes
