from app.services.app_marketplace_app_app_badge_collection import build_badge, build_badge_group

def test_badge():
    r = build_badge(label="New", variant="primary", icon="✨")
    assert r["label"] == "New"
    assert "blue" in r["classes"]
    assert r["icon"] == "✨"

def test_removable():
    r = build_badge(label="Tag", removable=True)
    assert r["removable"]

def test_group():
    badges = [{"label": "v2.0"}, {"label": "Featured", "variant": "success"}]
    r = build_badge_group(badges=badges)
    assert r["total"] == 2
    assert "green" in r["badges"][1]["classes"]
