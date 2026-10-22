"""Developer changelog builder — compile a developer's complete changelog."""


def build_developer_changelog(apps_with_versions: list[dict]) -> list[dict]:
    """Build unified changelog from all apps."""
    entries = []
    for app in apps_with_versions:
        for ver in app.get("versions", []):
            entries.append({
                "app_name": app.get("name"),
                "app_slug": app.get("slug"),
                "version": ver.get("version"),
                "changelog": ver.get("changelog", ""),
                "created_at": ver.get("created_at", ""),
            })
    return sorted(entries, key=lambda e: e.get("created_at", ""), reverse=True)
