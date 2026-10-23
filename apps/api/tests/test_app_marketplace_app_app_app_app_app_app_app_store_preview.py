from app.services.app_marketplace_app_app_app_app_app_app_app_store_preview import build_listing_preview

def test_preview():
    r = build_listing_preview({
        "name": "Slack Bot", "icon": "💬", "tagline": "The best Slack integration",
        "rating": 4.8, "installs": 50000, "price_type": "free", "verified": True,
        "category": "communication", "description": "A" * 60,
        "screenshots": ["s1.png"], "privacy_url": "https://example.com/privacy"})
    assert r["card_preview"]["name"] == "Slack Bot"
    assert r["card_preview"]["installs_display"] == "50,000"
    assert r["completeness"]["ready"]
    assert r["completeness"]["pct"] == 100

def test_incomplete():
    r = build_listing_preview({"name": "Test"})
    assert not r["completeness"]["ready"]
    assert r["completeness"]["pct"] < 50
