from app.services.app_developer_profile import build_public_profile

DEV = {"display_name": "Cool Dev", "slug": "cool-dev", "website_url": "https://x.com", "verified": True}
APPS = [
    {"id": "a1", "name": "App1", "slug": "app1", "status": "published", "category": "connector", "install_count": 50},
    {"id": "a2", "name": "App2", "slug": "app2", "status": "published", "category": "automation", "install_count": 30},
    {"id": "a3", "name": "Draft", "slug": "draft", "status": "draft", "category": "analytics"},
]

def test_basic():
    p = build_public_profile(developer=DEV, apps=APPS)
    assert p["display_name"] == "Cool Dev"
    assert p["verified"] is True

def test_only_published():
    p = build_public_profile(developer=DEV, apps=APPS)
    assert p["app_count"] == 2

def test_total_installs():
    p = build_public_profile(developer=DEV, apps=APPS)
    assert p["total_installs"] == 80

def test_categories():
    p = build_public_profile(developer=DEV, apps=APPS)
    assert "connector" in p["categories"]
    assert "analytics" not in p["categories"]  # draft excluded

def test_app_list():
    p = build_public_profile(developer=DEV, apps=APPS)
    assert len(p["apps"]) == 2
    assert p["apps"][0]["name"] == "App1"
