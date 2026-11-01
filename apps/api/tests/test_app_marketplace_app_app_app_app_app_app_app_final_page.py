from app.services.app_marketplace_app_app_app_app_app_app_app_final_page import build_complete_app_page

def test_page():
    r = build_complete_app_page({
        "name": "Slack Bot", "icon": "💬", "tagline": "Best Slack",
        "developer": "Acme", "rating": 4.8, "installs": 125000,
        "verified": True, "price_type": "free", "version": "3.2",
        "category": "communication",
    })
    assert r["hero"]["name"] == "Slack Bot"
    assert len(r["tabs"]) == 5
    assert r["sidebar"]["price_display"] == "Free"
    assert r["meta"]["category"] == "communication"
