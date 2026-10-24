from app.services.app_marketplace_app_app_app_welcome_screen import build_welcome_screen

def test_welcome():
    r = build_welcome_screen(app_name="SuperApp", app_icon="🚀")
    assert "SuperApp" in r["headline"]
    assert r["app_icon"] == "🚀"
    assert len(r["features"]) == 3
    assert len(r["next_steps"]) == 3
    assert r["dismissible"]

def test_custom():
    features = [{"title": "Custom", "description": "Feature", "icon": "✨"}]
    r = build_welcome_screen(app_name="X", features=features)
    assert len(r["features"]) == 1
