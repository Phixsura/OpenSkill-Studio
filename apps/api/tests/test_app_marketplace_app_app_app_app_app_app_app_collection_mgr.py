from app.services.app_marketplace_app_app_app_app_app_app_app_collection_mgr import create_collection, build_collection_page, add_to_collection

def test_create():
    c = create_collection(title="DevOps Essentials", description="Must-have DevOps tools",
                            curator="admin", app_ids=["app1", "app2", "app3"], featured=True)
    assert c["title"] == "DevOps Essentials"
    assert c["app_count"] == 3
    assert c["featured"]

def test_page():
    r = build_collection_page([
        {"app_count": 5, "featured": True},
        {"app_count": 3, "featured": False},
    ])
    assert r["total_collections"] == 2
    assert r["featured_count"] == 1
    assert r["total_apps"] == 8

def test_add():
    c = create_collection(title="Test", description="", curator="x", app_ids=["a"])
    r = add_to_collection(c, "b")
    assert r["app_count"] == 2
    r2 = add_to_collection(c, "a")
    assert "error" in r2
