from app.services.app_marketplace_app_app_app_app_app_app_app_badge_builder import build_badge, build_status_badge

def test_badge():
    b = build_badge(label="Pro", variant="primary", icon="⭐")
    assert b["label"] == "Pro"
    assert "blue" in b["classes"]
    assert b["icon"] == "⭐"

def test_status():
    b = build_status_badge("active")
    assert b["label"] == "Active"
    assert b["variant"] == "success"
    assert b["dot"]
    b2 = build_status_badge("error")
    assert b2["variant"] == "danger"
