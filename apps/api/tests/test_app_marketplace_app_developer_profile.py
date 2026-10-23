from app.services.app_marketplace_app_developer_profile import build_developer_profile

def test_profile():
    dev = {"id": "d1", "display_name": "Alice Dev", "bio": "Building cool stuff",
           "avatar": "alice.png", "joined": "2024-01-01", "verified": True}
    apps = [
        {"id": "a1", "name": "App A", "installs": 5000, "rating": 4.5, "category": "tools"},
        {"id": "a2", "name": "App B", "installs": 2000, "rating": 4.0, "category": "design"},
    ]
    r = build_developer_profile(developer=dev, apps=apps)
    assert r["display_name"] == "Alice Dev"
    assert r["stats"]["total_installs"] == 7000
    assert r["stats"]["avg_rating"] == 4.2
    assert r["verified"]
    assert r["top_apps"][0]["name"] == "App A"

def test_xss():
    dev = {"id": "d1", "display_name": "<script>alert(1)</script>", "bio": "a&b"}
    r = build_developer_profile(developer=dev, apps=[])
    assert "<script>" not in r["display_name"]
    assert "&amp;" in r["bio"]
