"""Complete docs page — documentation viewer with sidebar, search, and versioning."""


def build_complete_docs_page(*, app: dict, pages: list[dict], current_page: dict | None,
                                 api_version: str, search_query: str | None = None) -> dict:
    sidebar = []
    for p in pages:
        sidebar.append({"slug": p["slug"], "title": p["title"], "order": p.get("order", 0),
                          "children": p.get("children", [])})
    sidebar.sort(key=lambda x: x["order"])
    return {
        "page_type": "documentation",
        "app": {"id": app["id"], "name": app["name"]},
        "sidebar": sidebar,
        "current_page": current_page,
        "api_version": api_version,
        "total_pages": len(pages),
        "search_query": search_query,
        "has_search_results": search_query is not None,
    }
