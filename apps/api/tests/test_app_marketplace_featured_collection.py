from app.services.app_marketplace_featured_collection import create_collection, publish_collection, build_collection_card

def test_create():
    c = create_collection(title="Best Tools", description="Top picks", slug="best-tools",
                          apps=[{"id": f"a{i}"} for i in range(5)], curator_id="u1")
    assert c["app_count"] == 5
    assert c["status"] == "draft"

def test_publish_ok():
    c = {"app_count": 5, "slug": "s", "title": "T"}
    r = publish_collection(collection=c)
    assert r["published"]

def test_publish_too_few():
    r = publish_collection(collection={"app_count": 1})
    assert not r["published"]

def test_card():
    c = build_collection_card(
        collection={"slug": "best", "title": "Best", "description": "Top", "app_count": 3},
        apps=[{"id": "a1", "name": "App1", "icon": "🔧"}, {"id": "a2", "name": "App2"}])
    assert len(c["preview_apps"]) == 2
    assert c["preview_apps"][0]["icon"] == "🔧"
