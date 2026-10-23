from app.services.app_marketplace_app_app_app_app_app_app_search_page import build_search_results_page

def test_search():
    results = [
        {"id": "a1", "name": "Code Editor", "category": "tools", "rating": 4.5, "downloads": 5000},
        {"id": "a2", "name": "Chat Bot", "category": "communication", "rating": 4.0, "downloads": 3000},
    ]
    r = build_search_results_page(query="app", results=results)
    assert r["total"] == 2
    assert r["has_results"]
    assert "tools" in r["categories"]

def test_category_filter():
    results = [{"id": "a1", "category": "tools"}, {"id": "a2", "category": "comms"}]
    r = build_search_results_page(query="x", results=results, category="tools")
    assert r["total"] == 1

def test_empty():
    r = build_search_results_page(query="zzz", results=[])
    assert not r["has_results"]
