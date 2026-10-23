"""Social proof — testimonials and trust badges for landing pages."""

import html


def build_social_proof(*, testimonials: list[dict], logos: list[dict] | None = None,
                         stats: dict | None = None) -> dict:
    items = [{"quote": html.escape(t.get("quote", "")),
              "author": html.escape(t.get("author", "")),
              "role": html.escape(t.get("role", "")),
              "company": html.escape(t.get("company", "")),
              "avatar": t.get("avatar")} for t in testimonials[:6]]
    trust_logos = [{"name": html.escape(l.get("name", "")),
                     "url": l.get("url", "")} for l in (logos or [])]
    default_stats = {"developers": "1,800+", "apps": "5,200+",
                      "downloads": "12.5M+", "uptime": "99.99%"}
    return {"testimonials": items, "logos": trust_logos,
            "stats": stats or default_stats,
            "testimonial_count": len(items)}
