"""Developer newsletter — generate and manage developer newsletters."""

import html
import secrets
from datetime import datetime


def create_newsletter(*, title: str, sections: list[dict], edition: int) -> dict:
    safe_title = html.escape(title)
    rendered = []
    for sec in sections:
        rendered.append({
            "heading": html.escape(sec.get("heading", "")),
            "body": html.escape(sec.get("body", "")),
            "cta_label": sec.get("cta_label"),
            "cta_url": sec.get("cta_url"),
        })
    return {
        "newsletter_id": f"nl_{secrets.token_urlsafe(8)}",
        "title": safe_title,
        "edition": edition,
        "sections": rendered,
        "section_count": len(rendered),
        "created_at": datetime.utcnow().isoformat(),
        "status": "draft",
    }


def get_newsletter_stats(*, newsletters: list[dict]) -> dict:
    total = len(newsletters)
    total_sent = sum(n.get("sent_count", 0) for n in newsletters)
    total_opened = sum(n.get("opened_count", 0) for n in newsletters)
    avg_open_rate = round(total_opened / max(total_sent, 1) * 100, 1)
    return {"total_newsletters": total, "total_sent": total_sent,
            "total_opened": total_opened, "avg_open_rate": avg_open_rate}
