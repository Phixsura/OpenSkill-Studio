"""Banner carousel — rotating promotional banners."""

import html


def build_carousel(*, banners: list[dict]) -> dict:
    enriched = []
    for i, banner in enumerate(banners):
        enriched.append({
            "index": i,
            "title": html.escape(banner.get("title", "")),
            "subtitle": html.escape(banner.get("subtitle", "")),
            "cta_label": banner.get("cta_label", "Learn More"),
            "cta_url": banner.get("cta_url", "#"),
            "bg_gradient": banner.get("bg_gradient", "from-blue-600 to-purple-600"),
            "image_url": banner.get("image_url"),
        })
    return {"banners": enriched, "total": len(enriched), "auto_rotate": len(enriched) > 1,
            "rotate_interval_ms": 5000}
