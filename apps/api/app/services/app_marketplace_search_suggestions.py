"""Marketplace search suggestions — autocomplete for app search."""

_index: dict[str, list[str]] = {}


def build_suggestion_index(apps: list[dict]) -> None:
    """Build prefix index from app names and categories."""
    global _index
    _index.clear()
    for app in apps:
        for field in ["name", "category", "slug"]:
            text = app.get(field, "").lower()
            for i in range(1, len(text) + 1):
                prefix = text[:i]
                if prefix not in _index:
                    _index[prefix] = []
                if app.get("name") not in _index[prefix]:
                    _index[prefix].append(app.get("name", ""))


def get_suggestions(query: str, *, limit: int = 5) -> list[str]:
    prefix = query.lower().strip()
    if not prefix:
        return []
    matches = _index.get(prefix, [])
    return sorted(set(matches))[:limit]
