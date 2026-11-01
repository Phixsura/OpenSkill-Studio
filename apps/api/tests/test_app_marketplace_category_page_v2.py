from app.services.app_marketplace_category_page_v2 import build_category_page_v2

def test_page():
    apps = [{"name": f"App{i}", "install_count": i * 100, "avg_rating": 4.0} for i in range(30)]
    p = build_category_page_v2(
        category={"id": "connector", "name": "Connectors", "icon": "🔗", "description": "Integration tools"},
        apps=apps, subcategories=[{"id": "crm", "name": "CRM"}], page=1, per_page=10, sort_by="popular")
    assert p["page_type"] == "category_v2"
    assert len(p["apps"]) == 10
    assert p["pagination"]["total_pages"] == 3
    assert p["apps"][0]["install_count"] == 2900  # most popular first
    assert "Connectors" in p["seo"]["title"]

def test_empty():
    p = build_category_page_v2(category={"id": "x", "name": "X"}, apps=[], subcategories=[])
    assert p["pagination"]["total"] == 0
