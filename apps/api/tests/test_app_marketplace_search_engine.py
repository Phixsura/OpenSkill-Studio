from app.services.app_marketplace_search_engine import (
    SearchEngine, SearchableItem, SortBy,
)


def _make_engine() -> SearchEngine:
    engine = SearchEngine()
    engine.index(SearchableItem("e1", "extension", "Code Formatter", "Format code automatically",
                                 ["formatting", "code"], "tools", "alice", 5000, 4.5))
    engine.index(SearchableItem("e2", "extension", "Dark Theme", "Beautiful dark theme",
                                 ["theme", "ui"], "appearance", "bob", 12000, 4.8))
    engine.index(SearchableItem("c1", "connector", "Slack Notifier", "Send notifications to Slack",
                                 ["slack", "notifications"], "messaging", "carol", 8000, 4.2))
    return engine


def test_basic_search():
    engine = _make_engine()
    results = engine.search("formatter")
    assert len(results) >= 1
    assert results[0]["item"].item_id == "e1"
    assert results[0]["score"] > 0


def test_search_by_tag():
    engine = _make_engine()
    results = engine.search("slack")
    assert any(r["item"].item_id == "c1" for r in results)


def test_filter_by_type():
    engine = _make_engine()
    results = engine.search("", item_type="connector")
    assert all(r["item"].item_type == "connector" for r in results)


def test_filter_by_category():
    engine = _make_engine()
    results = engine.search("", category="appearance")
    assert len(results) == 1
    assert results[0]["item"].name == "Dark Theme"


def test_sort_by_popularity():
    engine = _make_engine()
    results = engine.search("", sort_by=SortBy.POPULARITY)
    downloads = [r["item"].downloads for r in results]
    assert downloads == sorted(downloads, reverse=True)


def test_suggest():
    engine = _make_engine()
    suggestions = engine.suggest("Co")
    assert "Code Formatter" in suggestions


def test_count():
    engine = _make_engine()
    assert engine.count() == 3
    assert engine.count("extension") == 2
    assert engine.count("connector") == 1
