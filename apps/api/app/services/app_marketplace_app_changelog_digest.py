"""Changelog digest — weekly/monthly summary of all platform changes."""


def build_changelog_digest(*, period: str, app_updates: list[dict],
                              platform_changes: list[str], deprecations: list[str]) -> dict:
    sections = []
    if app_updates:
        sections.append({"title": "App Updates", "items": [
            f"{u['app_name']} v{u['version']}" for u in app_updates[:10]
        ], "count": len(app_updates)})
    if platform_changes:
        sections.append({"title": "Platform Changes", "items": platform_changes})
    if deprecations:
        sections.append({"title": "Deprecations", "items": deprecations})
    return {"period": period, "sections": sections, "section_count": len(sections),
            "total_updates": len(app_updates) + len(platform_changes)}


def should_send_digest(*, subscriber_prefs: dict, digest_type: str) -> bool:
    return subscriber_prefs.get(f"{digest_type}_digest", True)
