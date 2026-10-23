from app.services.app_marketplace_app_app_category_grid import get_categories, get_category

def test_categories():
    r = get_categories()
    assert r["total_categories"] == 12
    assert r["total_apps"] > 400
    assert r["categories"][0]["count"] >= r["categories"][-1]["count"]  # sorted by count desc

def test_by_name():
    r = get_categories(sort_by="name")
    assert r["total_categories"] == 12

def test_get_one():
    r = get_category(category_id="security")
    assert r["name"] == "Security"
    assert r["icon"] == "🔒"

def test_not_found():
    r = get_category(category_id="magic")
    assert "error" in r
