from app.services.app_marketplace_app_app_gallery import build_gallery, get_collection_detail

def test_gallery():
    featured = [{"id": f"f{i}", "name": f"Featured {i}"} for i in range(8)]
    trending = [{"id": f"t{i}", "name": f"Trending {i}"} for i in range(4)]
    collections = [{"id": "c1", "title": "Best Tools", "app_count": 10, "icon": "🛠️"}]
    r = build_gallery(featured=featured, collections=collections, trending=trending)
    assert len(r["sections"]) == 2
    assert len(r["sections"][0]["apps"]) == 6  # capped
    assert r["total_collections"] == 1

def test_collection():
    coll = {"id": "c1", "title": "Security", "description": "Security apps", "curator": "Team"}
    apps = [{"id": "a1", "name": "Auth"}]
    r = get_collection_detail(collection=coll, apps=apps)
    assert r["app_count"] == 1
    assert r["curator"] == "Team"
