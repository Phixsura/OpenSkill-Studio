from app.services.app_marketplace_app_app_app_integration_card import build_integration_card, build_integrations_grid

def test_card():
    r = build_integration_card(integration_id="github", connected=True)
    assert r["label"] == "GitHub"
    assert r["connected"]
    assert r["cta"] == "Disconnect"

def test_not_connected():
    r = build_integration_card(integration_id="slack", connected=False)
    assert r["cta"] == "Connect"

def test_unknown():
    r = build_integration_card(integration_id="nonexistent")
    assert "error" in r

def test_grid():
    r = build_integrations_grid(connected=["github", "slack"])
    assert r["total"] == 8
    assert r["connected"] == 2
    assert r["available"] == 6
    assert len(r["categories"]) >= 5
