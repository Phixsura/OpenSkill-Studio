from app.services.app_marketplace_app_marketplace_theme import get_theme, get_css_variables, detect_preferred_theme, list_themes

def test_light():
    t = get_theme(theme_id="light")
    assert t["bg"] == "#ffffff"

def test_dark():
    t = get_theme(theme_id="dark")
    assert t["bg"] == "#111827"

def test_css_vars():
    v = get_css_variables(theme_id="light")
    assert "--color-bg" in v
    assert "--color-primary" in v

def test_detect_user():
    assert detect_preferred_theme(system_preference="light", user_preference="dark") == "dark"

def test_detect_system():
    assert detect_preferred_theme(system_preference="dark", user_preference=None) == "dark"

def test_detect_default():
    assert detect_preferred_theme(system_preference=None, user_preference=None) == "light"

def test_list():
    t = list_themes()
    assert len(t) == 3
