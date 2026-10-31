"""Not found page — user-friendly 404 pages for marketplace."""


def build_not_found_page(*, resource_type: str, search_query: str | None = None) -> dict:
    messages = {
        "app": {"title": "App Not Found", "message": "The app you're looking for doesn't exist or has been removed.",
                "suggestions": ["Check the URL", "Browse the marketplace", "Search for similar apps"]},
        "developer": {"title": "Developer Not Found", "message": "This developer profile doesn't exist.",
                       "suggestions": ["Check the URL", "Browse developers"]},
        "collection": {"title": "Collection Not Found", "message": "This collection doesn't exist or has been archived.",
                         "suggestions": ["Browse collections", "Explore featured apps"]},
        "page": {"title": "Page Not Found", "message": "We couldn't find what you're looking for.",
                  "suggestions": ["Go to the homepage", "Try searching"]},
    }
    config = messages.get(resource_type, messages["page"])
    return {
        "page_type": "not_found", "status_code": 404,
        **config, "icon": "🔍",
        "search_query": search_query,
        "actions": [
            {"label": "Go Home", "url": "/marketplace", "primary": True},
            {"label": "Search", "url": "/marketplace/search"},
        ],
    }
