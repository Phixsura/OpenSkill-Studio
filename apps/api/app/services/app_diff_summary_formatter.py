"""Diff summary formatter — human-readable diff summaries."""


def format_diff_summary(diff: dict) -> str:
    """Format a manifest diff as one-line summary."""
    parts = []
    added = diff.get("permissions", {}).get("added", [])
    removed = diff.get("permissions", {}).get("removed", [])
    if added: parts.append(f"+{len(added)} permissions")
    if removed: parts.append(f"-{len(removed)} permissions")
    if diff.get("sandbox", {}).get("changed"): parts.append("sandbox changed")
    if diff.get("config_schema_changed"): parts.append("config changed")
    events_added = diff.get("events", {}).get("added", [])
    if events_added: parts.append(f"+{len(events_added)} events")
    if diff.get("breaking"): parts.append("⚠️ BREAKING")
    return " · ".join(parts) if parts else "No changes"


def format_diff_markdown(diff: dict) -> str:
    """Format diff as markdown."""
    lines = []
    if diff.get("breaking"): lines.append("## ⚠️ Breaking Changes\n")
    added = diff.get("permissions", {}).get("added", [])
    removed = diff.get("permissions", {}).get("removed", [])
    if added: lines.append("### Permissions Added\n" + "\n".join(f"- `{p}`" for p in added))
    if removed: lines.append("### Permissions Removed\n" + "\n".join(f"- ~~`{p}`~~" for p in removed))
    return "\n\n".join(lines) if lines else "No changes"
