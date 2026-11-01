from app.services.app_marketplace_app_app_theme_config import build_theme_config

def test_defaults():
    r = build_theme_config()
    assert r["valid"]
    assert r["font"] == "Inter"
    assert "--color-primary" in r["css_vars"]

def test_custom():
    r = build_theme_config(primary="#FF0000", font="Roboto", border_radius=12)
    assert r["valid"]
    assert r["colors"]["primary"] == "#FF0000"

def test_invalid_color():
    r = build_theme_config(primary="red")
    assert not r["valid"]

def test_invalid_font():
    r = build_theme_config(font="Comic Sans")
    assert not r["valid"]
