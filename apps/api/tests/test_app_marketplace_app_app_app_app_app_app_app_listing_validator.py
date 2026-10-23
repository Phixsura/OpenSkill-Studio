from app.services.app_marketplace_app_app_app_app_app_app_app_listing_validator import validate_listing

def test_valid():
    r = validate_listing({
        "name": "My Great App", "description": "A" * 60,
        "icon": "📱", "category": "tools",
        "screenshots": ["s1.png"], "privacy_url": "https://example.com/privacy"})
    assert r["ready"]
    assert r["score"] == 100

def test_invalid():
    r = validate_listing({"name": "AB", "description": "short"})
    assert not r["ready"]
    assert r["score"] < 50
