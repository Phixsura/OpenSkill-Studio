"""Accordion — collapsible content sections."""


def build_accordion(*, sections: list[dict], allow_multiple: bool = False,
                      default_open: list[int] | None = None) -> dict:
    items = []
    for i, sec in enumerate(sections):
        items.append({
            "index": i,
            "title": sec.get("title", ""),
            "content": sec.get("content", ""),
            "icon": sec.get("icon"),
            "open": i in (default_open or []),
        })
    return {"items": items, "total": len(items),
            "allow_multiple": allow_multiple, "open_count": sum(1 for it in items if it["open"])}
