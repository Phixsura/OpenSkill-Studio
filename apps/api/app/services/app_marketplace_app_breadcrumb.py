"""Breadcrumb — generate navigation breadcrumbs from URL paths."""


ROUTE_MAP = {
    "": "Home",
    "apps": "Apps",
    "settings": "Settings",
    "analytics": "Analytics",
    "developers": "Developers",
    "webhooks": "Webhooks",
    "docs": "Documentation",
}


def build_breadcrumbs(*, path: str) -> dict:
    segments = [s for s in path.strip("/").split("/") if s]
    crumbs = [{"label": "Home", "path": "/", "active": len(segments) == 0}]
    accumulated = ""
    for i, seg in enumerate(segments):
        accumulated += f"/{seg}"
        label = ROUTE_MAP.get(seg, seg.replace("-", " ").replace("_", " ").title())
        is_last = i == len(segments) - 1
        crumbs.append({"label": label, "path": accumulated, "active": is_last})
    return {"breadcrumbs": crumbs, "depth": len(crumbs), "current": crumbs[-1]["label"]}
