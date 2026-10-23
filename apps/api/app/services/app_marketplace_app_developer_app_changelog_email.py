"""Changelog email — generate and send changelog notification emails to installers."""


def build_changelog_email(*, app_name: str, version: str, changes: list[dict],
                             recipients: int) -> dict:
    subject = f"{app_name} v{version} — What's New"
    sections = {"features": [], "fixes": [], "improvements": []}
    for c in changes:
        cat = c.get("type", "improvements")
        if cat in sections:
            sections[cat].append(c.get("description", ""))
    body_parts = [f"# {app_name} v{version}\n"]
    for cat, items in sections.items():
        if items:
            body_parts.append(f"\n## {cat.title()}\n")
            body_parts.extend(f"- {item}" for item in items)
    return {"subject": subject, "body": "\n".join(body_parts), "recipients": recipients,
            "has_features": len(sections["features"]) > 0}


def should_send_notification(*, change_types: list[str]) -> dict:
    important = {"features", "breaking", "security"}
    has_important = any(t in important for t in change_types)
    return {"should_send": has_important, "reason": "Contains important changes" if has_important else "Minor changes only"}
