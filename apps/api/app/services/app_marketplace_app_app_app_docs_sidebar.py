"""App docs sidebar — documentation sidebar navigation builder."""

import html


def build_docs_sidebar(*, sections: list[dict], active_path: str = "") -> dict:
    items = []
    for sec in sections:
        pages = []
        for p in sec.get("pages", []):
            pages.append({
                "title": html.escape(p.get("title", "")),
                "path": p.get("path", ""),
                "active": p.get("path", "") == active_path,
            })
        items.append({
            "title": html.escape(sec.get("title", "")),
            "icon": sec.get("icon", "📄"),
            "pages": pages,
            "page_count": len(pages),
            "expanded": any(pg["active"] for pg in pages),
        })
    total_pages = sum(s["page_count"] for s in items)
    return {"sections": items, "section_count": len(items),
            "total_pages": total_pages, "active_path": active_path}
