from app.services.app_marketplace_app_app_switch_toggle import build_toggle

def test_basic():
    r = build_toggle(label="Dark Mode", enabled=True, size="md")
    assert r["label"] == "Dark Mode"
    assert r["enabled"]
    assert r["dimensions"]["width"] == 44

def test_disabled():
    r = build_toggle(label="Feature X", disabled=True, description="Coming soon")
    assert r["disabled"]
    assert r["description"] == "Coming soon"
    assert "Toggle Feature X" in r["aria_label"]
