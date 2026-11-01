from app.services.app_marketplace_app_app_tag_cloud import build_tag_cloud

def test_cloud():
    apps = [
        {"tags": ["auth", "security", "api"]},
        {"tags": ["auth", "oauth"]},
        {"tags": ["api", "rest", "auth"]},
    ]
    r = build_tag_cloud(apps=apps, max_tags=5)
    assert r["tags"][0]["tag"] == "auth"  # most common
    assert r["tags"][0]["count"] == 3
    assert r["tags"][0]["weight"] == 100

def test_empty():
    r = build_tag_cloud(apps=[])
    assert r["total_unique"] == 0
