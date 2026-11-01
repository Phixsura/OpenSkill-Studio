"""Developer newsletter builder — compose and preview newsletters."""
from __future__ import annotations
import html


def build_newsletter(*, subject: str, sections: list[dict],
                       footer: str = "You're receiving this because you subscribed to OpenSkill updates.") -> dict:
    built = []
    for s in sections:
        built.append({
            "type": s.get("type", "text"),
            "title": html.escape(s.get("title", "")),
            "body": html.escape(s.get("body", "")[:1000]),
            "cta": s.get("cta", ""),
            "link": s.get("link", ""),
        })
    word_count = sum(len(s["body"].split()) for s in built)
    return {"subject": html.escape(subject), "sections": built,
            "section_count": len(built), "word_count": word_count,
            "read_time_min": max(1, word_count // 200),
            "footer": html.escape(footer)}
