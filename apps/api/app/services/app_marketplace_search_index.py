"""Marketplace search index — in-memory full-text search for apps."""

import re
from collections import defaultdict

_index: dict[str, set[str]] = defaultdict(set)  # term → set of app_ids
_docs: dict[str, dict] = {}  # app_id → app data


def index_app(app: dict) -> None:
    """Index an app for search."""
    app_id = app.get("id", "")
    _docs[app_id] = app
    text = f"{app.get('name', '')} {app.get('description', '')} {app.get('category', '')}".lower()
    tokens = set(re.findall(r'\w+', text))
    for token in tokens:
        _index[token].add(app_id)


def search(query: str, *, limit: int = 20) -> list[dict]:
    """Search indexed apps by query."""
    tokens = set(re.findall(r'\w+', query.lower()))
    if not tokens:
        return list(_docs.values())[:limit]
    
    scores: dict[str, int] = defaultdict(int)
    for token in tokens:
        for app_id in _index.get(token, set()):
            scores[app_id] += 1
    
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
    return [_docs[app_id] for app_id, _ in ranked if app_id in _docs]


def clear_index() -> None:
    _index.clear()
    _docs.clear()
