from app.services.app_marketplace_app_app_install_confirmation import build_install_confirmation

def test_safe():
    perms = [{"name": "read:profile", "risk": "low"}, {"name": "read:apps", "risk": "low"}]
    r = build_install_confirmation(app_name="Auth SDK", permissions=perms)
    assert r["max_risk"] == "low"
    assert not r["requires_review"]
    assert r["price_label"] == "Free"

def test_dangerous():
    perms = [{"name": "read:profile", "risk": "low"}, {"name": "admin:all", "risk": "critical"}]
    r = build_install_confirmation(app_name="Admin Tool", permissions=perms, price=29.99)
    assert r["max_risk"] == "critical"
    assert r["requires_review"]
    assert "$29.99" in r["price_label"]
    assert "⚠️" in r["confirm_message"]
