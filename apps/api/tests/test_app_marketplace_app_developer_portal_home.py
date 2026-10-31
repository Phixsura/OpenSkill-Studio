from app.services.app_marketplace_app_developer_portal_home import build_portal_home

def test_home():
    dev = {"display_name": "Alice"}
    apps = [
        {"id": "a1", "name": "Auth", "installs": 5000, "revenue": 2500, "rating": 4.5, "updated_at": "2026-10-23"},
        {"id": "a2", "name": "Charts", "installs": 3000, "revenue": 1500, "rating": 4.2, "updated_at": "2026-10-20"},
    ]
    r = build_portal_home(developer=dev, apps=apps, notifications=3)
    assert "Alice" in r["greeting"]
    assert r["stats"]["apps"] == 2
    assert r["stats"]["installs"] == 8000
    assert r["stats"]["revenue"] == 4000
    assert r["notifications"] == 3
    assert len(r["quick_links"]) == 6

def test_empty():
    r = build_portal_home(developer={}, apps=[], notifications=0)
    assert r["stats"]["apps"] == 0
