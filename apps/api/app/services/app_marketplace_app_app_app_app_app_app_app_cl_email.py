"""Changelog email builder — compose changelog digest emails."""
from __future__ import annotations
import html


def build_changelog_email(*, subject: str, version: str, changes: list[dict],
                             recipient_name: str = "Developer") -> dict:
    sections: dict[str, list[str]] = {}
    for c in changes:
        ctype = c.get("type", "changed")
        sections.setdefault(ctype, []).append(html.escape(c.get("text", "")))
    type_emoji = {"added": "✨", "fixed": "🐛", "changed": "🔄", "removed": "🗑️", "security": "🔒"}
    body_sections = []
    for t in ("added", "fixed", "changed", "security", "removed"):
        if t in sections:
            emoji = type_emoji.get(t, "📌")
            body_sections.append({"type": t, "emoji": emoji,
                                   "items": sections[t], "count": len(sections[t])})
    return {
        "subject": html.escape(subject), "version": version,
        "greeting": f"Hi {html.escape(recipient_name)},",
        "sections": body_sections, "total_changes": len(changes),
        "preview_text": f"{len(changes)} changes in v{version}",
    }
