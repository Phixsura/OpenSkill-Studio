from app.services.app_marketplace_app_app_color_mode import get_color_mode

def test_light():
    r = get_color_mode(preference="light")
    assert r["effective"] == "light"
    assert r["effective_bg"] == "#ffffff"

def test_dark():
    r = get_color_mode(preference="dark")
    assert r["effective"] == "dark"
    assert r["effective_bg"] == "#0a0a0a"

def test_system_dark():
    r = get_color_mode(preference="system", system_preference="dark")
    assert r["effective"] == "dark"
    assert r["preference"] == "system"

def test_modes():
    r = get_color_mode()
    assert len(r["available_modes"]) == 3
