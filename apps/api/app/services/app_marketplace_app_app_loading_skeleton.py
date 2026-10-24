"""Loading skeleton — skeleton screen configuration for loading states."""


def build_skeleton(*, layout: str = "card", count: int = 3) -> dict:
    LAYOUTS = {
        "card": {"rows": [{"type": "image", "height": 120}, {"type": "text", "lines": 2}, {"type": "badge", "count": 3}]},
        "list": {"rows": [{"type": "avatar", "size": 40}, {"type": "text", "lines": 1}, {"type": "badge", "count": 1}]},
        "table": {"rows": [{"type": "text", "lines": 1}] * 4},
        "profile": {"rows": [{"type": "avatar", "size": 80}, {"type": "text", "lines": 3}, {"type": "badge", "count": 4}]},
    }
    tmpl = LAYOUTS.get(layout, LAYOUTS["card"])
    items = [{"index": i, "rows": tmpl["rows"]} for i in range(count)]
    return {"layout": layout, "items": items, "count": count, "animated": True}
