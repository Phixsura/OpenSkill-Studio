"""Breadcrumb v2 — smart breadcrumbs with context-aware navigation."""


def build_smart_breadcrumb(*, path_segments: list[str], labels: dict[str, str],
                              current_page: str) -> list[dict]:
    crumbs = [{"label": "Home", "url": "/", "active": False}]
    url_parts = []
    for seg in path_segments:
        url_parts.append(seg)
        url = "/" + "/".join(url_parts)
        label = labels.get(seg, seg.replace("-", " ").replace("_", " ").title())
        is_active = seg == path_segments[-1]
        crumbs.append({"label": label, "url": url if not is_active else None, "active": is_active})
    return crumbs


def get_structured_breadcrumb(*, crumbs: list[dict]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": c["label"],
             "item": c["url"] or ""} for i, c in enumerate(crumbs)
        ],
    }
