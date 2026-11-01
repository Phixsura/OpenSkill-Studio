"""Marketplace sort options."""

SORT_OPTIONS = {
    "relevance": {"label": "Most Relevant", "field": "score", "order": "desc"},
    "installs": {"label": "Most Installed", "field": "install_count", "order": "desc"},
    "newest": {"label": "Newest First", "field": "created_at", "order": "desc"},
    "name": {"label": "Alphabetical", "field": "name", "order": "asc"},
    "rating": {"label": "Highest Rated", "field": "rating", "order": "desc"},
}

def get_sort_config(sort_by: str) -> dict:
    return SORT_OPTIONS.get(sort_by, SORT_OPTIONS["relevance"])

def list_sort_options() -> list[dict]:
    return [{"key": k, **v} for k, v in SORT_OPTIONS.items()]
