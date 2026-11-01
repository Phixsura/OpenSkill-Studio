"""Changelog formatter — generate human-readable changelogs."""


def format_release_notes(*, version: str, changes: list[dict], breaking: bool = False) -> str:
    """Format release notes for a version."""
    lines = [f"## v{version}{'  ⚠️ BREAKING' if breaking else ''}\n"]
    for change in changes:
        icon = {"added": "✨", "changed": "🔄", "fixed": "🐛", "removed": "🗑️", "security": "🔒"}.get(change.get("type", ""), "•")
        lines.append(f"- {icon} {change.get('description', '')}")
    return "\n".join(lines)


def format_full_changelog(releases: list[dict]) -> str:
    """Format a full changelog from multiple releases."""
    sections = []
    for release in releases:
        sections.append(format_release_notes(
            version=release["version"], changes=release.get("changes", []),
            breaking=release.get("breaking", False),
        ))
    return "\n\n".join(sections)
