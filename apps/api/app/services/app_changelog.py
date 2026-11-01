"""App changelog service — generates formatted changelogs from version diffs."""

from app.services.app_version_diff import diff_manifests


def generate_changelog_entry(
    *,
    version: str,
    old_manifest: dict | None,
    new_manifest: dict,
    changelog_text: str | None = None,
) -> dict:
    """Generate a changelog entry for a version.

    Returns a structured entry with diff summary and optional notes.
    """
    diff = diff_manifests(old_manifest or {}, new_manifest) if old_manifest else None

    entry = {
        "version": version,
        "notes": changelog_text or "",
        "breaking": diff["breaking"] if diff else False,
        "changes": [],
    }

    if diff:
        if diff["permissions"]["added"]:
            entry["changes"].append({
                "type": "permissions_added",
                "items": diff["permissions"]["added"],
            })
        if diff["permissions"]["removed"]:
            entry["changes"].append({
                "type": "permissions_removed",
                "items": diff["permissions"]["removed"],
                "breaking": True,
            })
        if diff["events"]["added"]:
            entry["changes"].append({
                "type": "events_added",
                "items": diff["events"]["added"],
            })
        if diff["secrets"]["added"]:
            entry["changes"].append({
                "type": "secrets_added",
                "items": diff["secrets"]["added"],
            })
        if diff["ui_extensions"]["added"]:
            entry["changes"].append({
                "type": "ui_extensions_added",
                "items": diff["ui_extensions"]["added"],
            })
        if diff["sandbox"]["changed"]:
            entry["changes"].append({"type": "sandbox_changed"})
        if diff["config_schema_changed"]:
            entry["changes"].append({"type": "config_schema_changed"})

    return entry


def format_changelog_markdown(entries: list[dict]) -> str:
    """Format changelog entries as Markdown."""
    lines = ["# Changelog\n"]
    for entry in entries:
        breaking = " ⚠️ BREAKING" if entry.get("breaking") else ""
        lines.append(f"## {entry['version']}{breaking}\n")
        if entry.get("notes"):
            lines.append(f"{entry['notes']}\n")
        for change in entry.get("changes", []):
            ctype = change["type"].replace("_", " ").title()
            if "items" in change:
                lines.append(f"- **{ctype}**: {', '.join(change['items'])}")
            else:
                lines.append(f"- **{ctype}**")
        lines.append("")
    return "\n".join(lines)
