"""Changelog page v2 — platform-wide changelog across all services."""

import html
from datetime import datetime, timezone

SERVICES = ["API", "Web", "SDK", "CLI", "Webhooks", "Analytics", "Auth", "Billing"]


def build_platform_changelog(*, entries: list[dict], period: str = "30d") -> dict:
    by_service: dict[str, list] = {}
    for e in entries:
        svc = e.get("service", "Platform")
        by_service.setdefault(svc, []).append({
            "title": html.escape(e.get("title", "")),
            "type": e.get("type", "changed"),
            "date": e.get("date", ""),
            "icon": {"added": "✨", "fixed": "🐛", "changed": "🔄", "removed": "🗑️",
                      "security": "🔒", "performance": "⚡"}.get(e.get("type", ""), "📌"),
        })
    sections = [{"service": svc, "entries": items, "count": len(items)}
                for svc, items in sorted(by_service.items())]
    return {"sections": sections, "total_entries": len(entries),
            "service_count": len(sections), "period": period,
            "services": SERVICES}
