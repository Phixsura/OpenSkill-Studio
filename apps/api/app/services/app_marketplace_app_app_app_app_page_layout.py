"""App page layout — complete page layout builder with header, sidebar, content."""

import html


def build_page_layout(*, page_title: str, breadcrumbs: list[dict],
                         sidebar_items: list[dict], user: dict | None = None,
                         notifications: int = 0) -> dict:
    crumbs = [{"label": html.escape(b.get("label", "")), "href": b.get("href")}
              for b in breadcrumbs]
    nav = [{"label": html.escape(s.get("label", "")), "href": s.get("href", "#"),
            "icon": s.get("icon", "📄"), "active": s.get("active", False),
            "badge": s.get("badge")} for s in sidebar_items]
    return {
        "page_title": html.escape(page_title),
        "breadcrumbs": crumbs,
        "sidebar": nav,
        "user": {"name": html.escape(user.get("name", "")),
                  "initials": "".join(w[0].upper() for w in user.get("name", "?").split()[:2])}
                if user else None,
        "notifications": notifications,
        "has_sidebar": len(nav) > 0,
    }
