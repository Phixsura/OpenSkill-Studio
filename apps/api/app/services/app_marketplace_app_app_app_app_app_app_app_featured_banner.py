"""Featured banner — promotional banners for the marketplace homepage."""
from __future__ import annotations
import html


def build_featured_banners(banners: list[dict]) -> dict:
    items = []
    for b in banners:
        items.append({
            "title": html.escape(b.get("title", "")),
            "subtitle": html.escape(b.get("subtitle", "")[:150]),
            "cta": b.get("cta", "Learn More"),
            "link": b.get("link", ""),
            "bg_gradient": b.get("gradient", "from-blue-600 to-purple-600"),
            "icon": b.get("icon", "🚀"),
        })
    return {"banners": items, "count": len(items)}
