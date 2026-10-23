"""Breadcrumb builder — generic breadcrumb construction for all marketplace pages."""


def build_breadcrumb(*, segments: list[dict]) -> list[dict]:
    crumbs = [{"label": "Home", "url": "/"}]
    crumbs.extend(segments)
    return crumbs


def build_marketplace_breadcrumb(*, page_type: str, context: dict) -> list[dict]:
    segments = [{"label": "Marketplace", "url": "/marketplace"}]
    if page_type == "category":
        segments.append({"label": context.get("category_name", ""), "url": f"/marketplace/category/{context.get('category_id', '')}"})
    elif page_type == "app":
        if context.get("category_name"):
            segments.append({"label": context["category_name"], "url": f"/marketplace/category/{context.get('category_id', '')}"})
        segments.append({"label": context.get("app_name", ""), "url": f"/marketplace/apps/{context.get('app_slug', '')}"})
    elif page_type == "developer":
        segments.append({"label": context.get("developer_name", ""), "url": f"/marketplace/developers/{context.get('developer_slug', '')}"})
    elif page_type == "collection":
        segments.append({"label": context.get("collection_title", ""), "url": f"/marketplace/collections/{context.get('collection_slug', '')}"})
    return build_breadcrumb(segments=segments)
