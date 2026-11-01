"""Changelog email — generate changelog notification emails."""

import html


def generate_changelog_email(*, app_name: str, version: str, changes: list[dict],
                                recipient_count: int) -> dict:
    safe_name = html.escape(app_name)
    sections = {}
    for c in changes:
        ctype = c.get("type", "other")
        sections.setdefault(ctype, []).append(html.escape(c.get("description", "")))
    subject = f"{safe_name} v{html.escape(version)} Released"
    body_parts = [f"<h2>{safe_name} v{html.escape(version)}</h2>"]
    type_labels = {"feature": "🚀 New Features", "fix": "🐛 Bug Fixes",
                    "improvement": "✨ Improvements", "breaking": "⚠️ Breaking Changes"}
    for ctype, items in sections.items():
        label = type_labels.get(ctype) or html.escape(str(ctype).title())
        body_parts.append(f"<h3>{label}</h3><ul>")
        for item in items:
            body_parts.append(f"<li>{item}</li>")
        body_parts.append("</ul>")
    return {
        "subject": subject,
        "body_html": "\n".join(body_parts),
        "recipient_count": recipient_count,
        "change_count": len(changes),
        "has_breaking": "breaking" in sections,
    }
