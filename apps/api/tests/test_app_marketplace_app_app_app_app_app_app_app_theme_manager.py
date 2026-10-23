from app.services.app_marketplace_app_app_app_app_app_app_app_theme_manager import get_theme, create_custom_theme, list_presets, validate_color

def test_theme():
    t = get_theme("dark")
    assert t["colors"]["bg"] == "#111827"
    assert t["token_count"] == 8

def test_custom():
    r = create_custom_theme(name="brand", base="light", overrides={"primary": "#FF5500"})
    assert r["colors"]["primary"] == "#FF5500"
    assert r["colors"]["bg"] == "#FFFFFF"  # inherited

def test_invalid():
    r = create_custom_theme(name="bad", overrides={"primary": "notacolor"})
    assert "error" in r

def test_presets():
    p = list_presets()
    assert len(p) == 3
    assert validate_color("#FF0000")
    assert not validate_color("red")
