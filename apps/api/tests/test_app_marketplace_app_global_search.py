from app.services.app_marketplace_app_global_search import global_search

def test_search():
    catalogs = {
        "apps": [{"id": "a1", "name": "Auth SDK"}, {"id": "a2", "name": "Payment Gateway"}],
        "docs": [{"id": "d1", "title": "Auth Guide"}, {"id": "d2", "title": "API Reference"}],
    }
    r = global_search(query="auth", catalogs=catalogs)
    assert r["total"] == 2  # Auth SDK + Auth Guide
    assert r["by_category"]["apps"] == 1
    assert r["by_category"]["docs"] == 1

def test_too_short():
    r = global_search(query="a", catalogs={"apps": [{"name": "Auth"}]})
    assert r["total"] == 0

def test_no_match():
    r = global_search(query="zzz", catalogs={"apps": [{"name": "Auth"}]})
    assert r["total"] == 0
