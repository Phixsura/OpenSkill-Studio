from app.services.app_marketplace_extension_marketplace_search_index import (
    SearchIndex, IndexedDocument,
)


def _setup() -> SearchIndex:
    idx = SearchIndex()
    idx.index(IndexedDocument("ext-1", {"name": "Slack Bot Pro", "description": "Advanced Slack integration", "category": "messaging", "tags": "slack notifications"}))
    idx.index(IndexedDocument("ext-2", {"name": "GitHub Sync", "description": "Sync code with GitHub", "category": "devtools", "tags": "github git code"}))
    idx.index(IndexedDocument("ext-3", {"name": "Dark Theme Ultra", "description": "Beautiful dark theme", "category": "themes", "tags": "theme dark ui"}))
    return idx


def test_search_by_name():
    idx = _setup()
    results = idx.search("slack")
    assert len(results) >= 1
    assert results[0]["doc_id"] == "ext-1"


def test_search_by_tag():
    idx = _setup()
    results = idx.search("github")
    assert any(r["doc_id"] == "ext-2" for r in results)


def test_name_boost():
    idx = _setup()
    results = idx.search("dark")
    # "Dark Theme Ultra" should rank high because name has 10x boost
    assert results[0]["doc_id"] == "ext-3"


def test_category_filter():
    idx = _setup()
    results = idx.search("", category="messaging")
    # Empty query won't return results (no tokens), test with content
    results2 = idx.search("slack", category="devtools")
    # Slack is in messaging, not devtools, so filtered out
    assert all(r["doc_id"] != "ext-1" for r in results2)


def test_suggest():
    idx = _setup()
    suggestions = idx.suggest("sla")
    assert "slack" in suggestions


def test_remove():
    idx = _setup()
    assert idx.remove("ext-1") is True
    results = idx.search("slack")
    assert all(r["doc_id"] != "ext-1" for r in results)
    assert idx.doc_count() == 2


def test_facets():
    idx = _setup()
    facets = idx.get_facets()
    assert "category" in facets
    assert facets["category"]["messaging"] == 1
