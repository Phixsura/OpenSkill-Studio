from app.services.app_marketplace_app_comparison import compare_apps

def test_compare():
    r = compare_apps([
        {"id": "a1", "name": "App A", "features": ["auth", "webhooks", "api"]},
        {"id": "a2", "name": "App B", "features": ["auth", "sandbox"]},
    ])
    assert r["total_features"] == 4
    assert r["common_features"] == 1  # auth
    assert len(r["matrix"]) == 4

def test_too_few():
    r = compare_apps([{"id": "a1", "name": "Solo"}])
    assert r["error"]

def test_no_features():
    r = compare_apps([{"id": "a1", "name": "A", "features": []}, {"id": "a2", "name": "B", "features": []}])
    assert r["total_features"] == 0
