from app.services.app_marketplace_app_app_search_filter import apply_filters, build_facets

ITEMS = [
    {"name": "AppA", "category": "tools", "rating": 4.5},
    {"name": "AppB", "category": "tools", "rating": 3.0},
    {"name": "AppC", "category": "games", "rating": 4.8},
]

def test_text_filter():
    r = apply_filters(items=ITEMS, filters={"name": "AppA"})
    assert r["total"] == 1

def test_list_filter():
    r = apply_filters(items=ITEMS, filters={"category": ["tools"]})
    assert r["total"] == 2

def test_range_filter():
    r = apply_filters(items=ITEMS, filters={"rating": {"min": 4.0}})
    assert r["total"] == 2

def test_facets():
    r = build_facets(items=ITEMS, facet_fields=["category"])
    assert r["facets"]["category"][0]["value"] == "tools"
    assert r["facets"]["category"][0]["count"] == 2
