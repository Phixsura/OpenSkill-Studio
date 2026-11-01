"""URL builder — construct canonical URLs for all marketplace entities."""

BASE_URL = "https://openskill.dev"


def build_app_url(*, slug: str) -> str:
    return f"{BASE_URL}/marketplace/apps/{slug}"


def build_developer_url(*, slug: str) -> str:
    return f"{BASE_URL}/marketplace/developers/{slug}"


def build_collection_url(*, slug: str) -> str:
    return f"{BASE_URL}/marketplace/collections/{slug}"


def build_category_url(*, category_id: str) -> str:
    return f"{BASE_URL}/marketplace/category/{category_id}"


def build_api_url(*, path: str, version: str = "v1") -> str:
    return f"{BASE_URL}/api/{version}{path}"


def build_docs_url(*, page: str) -> str:
    return f"{BASE_URL}/docs/{page}"


def build_search_url(*, query: str, filters: dict | None = None) -> str:
    from urllib.parse import urlencode
    params = {"q": query}
    if filters:
        params.update(filters)
    return f"{BASE_URL}/marketplace/search?{urlencode(params)}"
