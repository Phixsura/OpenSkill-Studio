from app.services.app_marketplace_comparison_v2 import compare_apps_v2

def test_compare():
    apps = [
        {"id": "a1", "name": "App A", "avg_rating": 4.5, "install_count": 500, "features": ["x", "y"]},
        {"id": "a2", "name": "App B", "avg_rating": 3.0, "install_count": 2000, "features": ["x"]},
    ]
    r = compare_apps_v2(apps=apps)
    assert len(r["rows"]) == 6
    assert r["winner"] is not None
    assert len(r["scores"]) == 2

def test_too_few():
    r = compare_apps_v2(apps=[{"id": "a1"}])
    assert r["error"]
