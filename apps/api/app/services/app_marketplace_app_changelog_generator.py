"""Marketplace app changelog generator — auto-generate changelog from version diffs."""

from app.services.app_version_diff import diff_manifests


def auto_generate_changelog(*, old_manifest: dict | None, new_manifest: dict, version: str) -> str:
    """Auto-generate changelog text from manifest diff."""
    if not old_manifest:
        return f"v{version}: Initial release"
    diff = diff_manifests(old_manifest, new_manifest)
    parts = []
    added_perms = diff.get("permissions", {}).get("added", [])
    if added_perms:
        parts.append(f"Added permissions: {', '.join(added_perms)}")
    removed_perms = diff.get("permissions", {}).get("removed", [])
    if removed_perms:
        parts.append(f"Removed permissions: {', '.join(removed_perms)}")
    if diff.get("sandbox", {}).get("changed"):
        parts.append("Updated sandbox configuration")
    events_added = diff.get("events", {}).get("added", [])
    if events_added:
        parts.append(f"Added event subscriptions: {', '.join(events_added)}")
    if not parts:
        parts.append("Minor updates")
    return f"v{version}: " + "; ".join(parts)
