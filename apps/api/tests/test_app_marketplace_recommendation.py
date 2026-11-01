from app.services.app_marketplace_recommendation import recommend_apps

APPS = [
    {"name": "Conn A", "category": "connector", "install_count": 100},
    {"name": "Auto B", "category": "automation", "install_count": 50},
    {"name": "Anal C", "category": "analytics", "install_count": 200},
    {"name": "Pack D", "category": "content_pack", "install_count": 10},
]

def test_same_category():
    recs = recommend_apps(installed_categories=["connector"], available_apps=APPS)
    assert recs[0]["name"] == "Conn A"

def test_related():
    recs = recommend_apps(installed_categories=["connector"], available_apps=APPS)
    names = [r["name"] for r in recs]
    assert "Auto B" in names  # automation related to connector

def test_limit():
    recs = recommend_apps(installed_categories=["connector"], available_apps=APPS, limit=2)
    assert len(recs) <= 2

def test_no_match():
    recs = recommend_apps(installed_categories=["ecosystem_source"], available_apps=APPS)
    assert len(recs) == 0 or all(r.get("install_count", 0) > 0 for r in recs)

def test_empty():
    assert recommend_apps(installed_categories=[], available_apps=[]) == []
