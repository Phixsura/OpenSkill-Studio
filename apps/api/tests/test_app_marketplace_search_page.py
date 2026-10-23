from app.services.app_marketplace_search_page import build_search_page, build_zero_results_page

def test_search_page():
    p = build_search_page(query="webhook", results=[{"id": "a1"}], total=50,
                            page=2, per_page=20, filters={"category": "connector"},
                            facets={"categories": {"connector": 30}}, suggestions=["webhooks"])
    assert p["page_type"] == "search_results"
    assert p["pagination"]["total_pages"] == 3
    assert p["pagination"]["has_prev"]
    assert not p["empty"]

def test_empty():
    p = build_search_page(query="xyz", results=[], total=0, page=1, per_page=20,
                            filters={}, facets={}, suggestions=[])
    assert p["empty"]

def test_zero():
    z = build_zero_results_page(query="xyzabc", suggestions=["xyz"], popular_apps=[{"id": "a1"}])
    assert z["page_type"] == "zero_results"
    assert len(z["tips"]) == 3
    assert z["did_you_mean"] == ["xyz"]
