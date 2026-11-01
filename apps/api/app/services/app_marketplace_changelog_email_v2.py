"""Changelog email v2 — rich email notifications for app updates with targeting."""


def build_changelog_email_v2(*, app: dict, version: dict, changes: list[dict],
                                  recipients: dict) -> dict:
    features = [c for c in changes if c.get("type") == "feat"]
    fixes = [c for c in changes if c.get("type") == "fix"]
    breaking = [c for c in changes if c.get("breaking")]
    subject = f"{app['name']} v{version['version']}"
    if breaking:
        subject += " ⚠️ Breaking Changes"
    elif features:
        subject += " — New Features!"
    sections = []
    if breaking:
        sections.append({"title": "Breaking Changes", "icon": "⚠️",
                          "items": [c["description"] for c in breaking]})
    if features:
        sections.append({"title": "New Features", "icon": "✨",
                          "items": [c["description"] for c in features]})
    if fixes:
        sections.append({"title": "Bug Fixes", "icon": "🐛",
                          "items": [c["description"] for c in fixes]})
    return {
        "subject": subject,
        "sections": sections,
        "total_changes": len(changes),
        "recipients": {
            "all_users": recipients.get("all_users", 0),
            "active_users": recipients.get("active_users", 0),
            "targeted": recipients.get("active_users", 0),
        },
        "cta": {"label": "View Changelog", "url": f"/marketplace/apps/{app.get('slug')}/changelog"},
    }


def should_send_email(*, changes: list[dict], min_changes: int = 1) -> dict:
    has_features = any(c.get("type") == "feat" for c in changes)
    has_breaking = any(c.get("breaking") for c in changes)
    should_send = len(changes) >= min_changes and (has_features or has_breaking)
    return {"send": should_send, "reason": "breaking" if has_breaking else "features" if has_features else "minor",
            "priority": "high" if has_breaking else "normal"}
