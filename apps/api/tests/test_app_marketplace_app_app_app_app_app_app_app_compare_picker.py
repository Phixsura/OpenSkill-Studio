from app.services.app_marketplace_app_app_app_app_app_app_app_compare_picker import build_compare_selection, find_similar_apps

def test_selection():
    r = build_compare_selection([
        {"id": "a", "name": "App A", "rating": 4.5},
        {"id": "b", "name": "App B", "rating": 4.2},
    ])
    assert r["count"] == 2
    assert r["can_compare"]
    assert r["can_add"]

def test_similar():
    all_apps = [
        {"id": "a", "category": "tools", "rating": 4.5},
        {"id": "b", "category": "tools", "rating": 4.8},
        {"id": "c", "category": "tools", "rating": 4.2},
        {"id": "d", "category": "analytics", "rating": 5.0},
    ]
    r = find_similar_apps({"id": "a", "category": "tools"}, all_apps)
    assert len(r) == 2
    assert r[0]["id"] == "b"  # highest rated first
