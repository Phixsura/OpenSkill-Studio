from app.services.app_marketplace_app_app_theme_token import get_tokens, generate_css_vars

def test_light():
    r = get_tokens(theme="light")
    assert r["tokens"]["bg-primary"] == "#ffffff"
    assert r["token_count"] == 11

def test_dark():
    r = get_tokens(theme="dark")
    assert r["tokens"]["bg-primary"] == "#0a0a0a"

def test_css():
    r = generate_css_vars(theme="light")
    assert "--bg-primary: #ffffff;" in r["css"]
    assert ":root {" in r["css"]
