from app.services.app_marketplace_app_app_app_app_app_app_app_category_mgr import get_categories, get_category, count_apps_by_category

def test_categories():
    cats = get_categories()
    assert len(cats) == 8
    assert cats[0]["id"] == "analytics"

def test_get():
    c = get_category("security")
    assert c is not None
    assert c["icon"] == "🔐"
    assert get_category("nope") is None

def test_count():
    apps = [{"category": "analytics"}, {"category": "analytics"}, {"category": "security"}]
    r = count_apps_by_category(apps)
    an = next(c for c in r if c["id"] == "analytics")
    assert an["count"] == 2
    sec = next(c for c in r if c["id"] == "security")
    assert sec["count"] == 1
