from app.services.app_marketplace_app_app_app_app_app_app_app_app_detail_page import build_app_detail

def test_detail():
    r = build_app_detail({
        "name": "Slack Bot Pro", "tagline": "Ultimate Slack integration",
        "description": "Connect your workflow with Slack",
        "long_description": "Detailed description of features...",
        "icon": "💬", "category": "communication",
        "developer": "Acme Corp", "rating": 4.8,
        "installs": 125000, "version": "3.2.1",
        "verified": True, "price_type": "free",
        "permissions": ["read:profile", "webhooks"],
        "tags": ["slack", "communication", "automation"],
        "review_count": 342,
    })
    assert r["name"] == "Slack Bot Pro"
    assert r["tagline"] == "Ultimate Slack integration"
    assert r["installs_display"] == "125,000"
    assert r["verified"]
    assert r["price_display"] == "Free"
    assert r["review_count"] == 342
    assert len(r["permissions"]) == 2
    assert len(r["tags"]) == 3
