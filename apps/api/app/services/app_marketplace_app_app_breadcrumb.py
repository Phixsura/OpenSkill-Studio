"""Breadcrumb — navigation trail builder."""

import html


def build_breadcrumb(*, items: list[dict]) -> dict:
    trail = []
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        trail.append({
            "label": html.escape(item["label"]),
            "href": item.get("href") if not is_last else None,
            "is_current": is_last,
        })
    return {"trail": trail, "depth": len(trail)}
