from app.services.app_marketplace_collection_v2 import create_collection_v2, build_collection_page, auto_curate_collection

def test_create():
    apps = [{"id": f"a{i}"} for i in range(5)]
    c = create_collection_v2(title="Best Tools", description="Top picks", slug="best-tools",
                               apps=apps, curator_id="u1")
    assert c["status"] == "published"
    assert c["app_count"] == 5

def test_draft():
    c = create_collection_v2(title="Small", description="X", slug="small", apps=[{"id": "a1"}], curator_id="u1")
    assert c["status"] == "draft"

def test_page():
    collection = {"title": "Best", "description": "Top apps"}
    p = build_collection_page(collection=collection, apps=[{"id": "a1"}], related=[{"title": "Other"}])
    assert "Best" in p["seo"]["title"]

def test_auto_trending():
    apps = [{"id": "a1", "trending_score": 10}, {"id": "a2", "trending_score": 50}]
    r = auto_curate_collection(apps=apps, criteria="trending")
    assert r[0]["id"] == "a2"

def test_auto_rated():
    apps = [{"id": "a1", "avg_rating": 3}, {"id": "a2", "avg_rating": 5}]
    r = auto_curate_collection(apps=apps, criteria="top_rated")
    assert r[0]["id"] == "a2"
