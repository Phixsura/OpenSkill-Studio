from app.services.app_marketplace_app_app_app_app_app_app_app_final_app_card import build_final_card

def test_card():
    r = build_final_card({
        "name": "Slack Bot Pro", "icon": "💬", "tagline": "The best Slack integration",
        "developer": "Acme Corp", "rating": 4.8, "installs": 125000,
        "price_type": "free", "verified": True, "category": "communication",
        "badges": ["verified", "top_rated"],
    })
    assert r["name"] == "Slack Bot Pro"
    assert r["installs_display"] == "125,000"
    assert r["verified"]
    assert r["price_display"] == "Free"
    assert len(r["badges"]) == 2
