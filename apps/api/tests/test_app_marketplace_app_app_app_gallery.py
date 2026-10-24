from app.services.app_marketplace_app_app_app_gallery import build_gallery

def test_gallery():
    collections = [
        {"title": "Top Rated", "icon": "⭐", "apps": [
            {"id": "a1", "name": "SuperApp"}, {"id": "a2", "name": "MegaTool"}]},
        {"title": "New", "icon": "🆕", "apps": [{"id": "a3", "name": "FreshApp"}]},
    ]
    r = build_gallery(collections=collections)
    assert r["total_collections"] == 2
    assert r["total_apps"] == 3
    assert r["collections"][0]["app_count"] == 2
