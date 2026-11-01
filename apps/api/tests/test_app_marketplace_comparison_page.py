from app.services.app_marketplace_comparison_page import build_comparison_page

def test_compare():
    apps = [
        {"id": "a1", "name": "App A", "rating": 4.5, "installs": 500, "price": "Free"},
        {"id": "a2", "name": "App B", "rating": 4.0, "installs": 2000, "price": "$9.99"},
    ]
    r = build_comparison_page(apps=apps)
    assert r["dimension_count"] == 8
    assert len(r["apps"]) == 2

def test_too_few():
    r = build_comparison_page(apps=[{"id": "a1"}])
    assert r["error"]

def test_too_many():
    r = build_comparison_page(apps=[{"id": f"a{i}", "name": f"App {i}"} for i in range(5)])
    assert r["error"]
