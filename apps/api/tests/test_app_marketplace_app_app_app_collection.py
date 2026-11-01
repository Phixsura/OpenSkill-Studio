from app.services.app_marketplace_app_app_app_collection import create_collection, build_collections_page

def test_create():
    r = create_collection(title="Best Tools", description="Top developer tools",
                           curator="Alice", apps=["a1", "a2", "a3"])
    assert r["id"].startswith("col_")
    assert r["app_count"] == 3

def test_page():
    cols = [
        {"title": "Featured", "featured": True, "app_count": 5},
        {"title": "New", "featured": False, "app_count": 3},
    ]
    r = build_collections_page(collections=cols)
    assert len(r["featured"]) == 1
    assert r["total_apps"] == 8
