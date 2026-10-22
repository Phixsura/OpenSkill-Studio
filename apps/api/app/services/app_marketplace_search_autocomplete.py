"""Search autocomplete — trie-based prefix matching for marketplace search."""


class SearchAutocomplete:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def index(self, items: list[dict]) -> None:
        self._items = items

    def suggest(self, query: str, limit: int = 5) -> list[dict]:
        if not query or len(query) < 2:
            return []
        q = query.lower()
        scored = []
        for item in self._items:
            name = item.get("name", "").lower()
            if name.startswith(q):
                scored.append((0, item))
            elif q in name:
                scored.append((1, item))
            elif any(q in tag.lower() for tag in item.get("tags", [])):
                scored.append((2, item))
        scored.sort(key=lambda x: (x[0], -item.get("install_count", 0)))
        return [s[1] for s in scored[:limit]]


def build_suggestions_response(*, suggestions: list[dict]) -> dict:
    return {
        "suggestions": [
            {"name": s["name"], "slug": s.get("slug"), "category": s.get("category"),
             "icon": s.get("icon"), "type": "app"} for s in suggestions
        ],
        "count": len(suggestions),
    }
