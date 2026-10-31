from app.services.app_marketplace_app_app_search_filter_chip import build_active_filters, remove_filter

def test_build():
    filters = {"category": "tools", "rating": "4+", "platform": ["web", "mobile"]}
    r = build_active_filters(filters=filters)
    assert r["active_count"] == 4  # category + rating + 2 platforms
    assert r["has_filters"]

def test_empty():
    r = build_active_filters(filters={})
    assert not r["has_filters"]

def test_remove():
    filters = {"category": "tools", "rating": "4+"}
    r = remove_filter(filters=filters, key="category")
    assert "category" not in r["filters"]
    assert "rating" in r["filters"]

def test_remove_from_list():
    filters = {"platform": ["web", "mobile"]}
    r = remove_filter(filters=filters, key="platform", value="web")
    assert r["filters"]["platform"] == ["mobile"]
