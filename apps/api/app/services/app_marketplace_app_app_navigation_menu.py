"""Navigation menu — sidebar and header nav builder."""

import html


def build_nav_menu(*, items: list[dict], active_path: str = "") -> dict:
    sections: dict[str, list] = {}
    for item in items:
        section = item.get("section", "main")
        entry = {
            "label": html.escape(item.get("label", "")),
            "path": item.get("path", "#"),
            "icon": item.get("icon", "📄"),
            "active": item.get("path", "") == active_path,
            "badge": item.get("badge"),
        }
        sections.setdefault(section, []).append(entry)
    flat = [e for entries in sections.values() for e in entries]
    return {"sections": sections, "section_count": len(sections),
            "total_items": len(flat), "active_path": active_path}
