from app.services.app_marketplace_app_app_select_input import build_select_config

def test_basic():
    options = [{"value": "us", "label": "United States"}, {"value": "gb", "label": "United Kingdom"}]
    r = build_select_config(name="country", label="Country", options=options, required=True)
    assert r["name"] == "country"
    assert r["option_count"] == 2
    assert r["required"]
    assert r["options"][0]["label"] == "United States"

def test_with_icons():
    options = [{"value": "light", "label": "Light", "icon": "☀️"},
               {"value": "dark", "label": "Dark", "icon": "🌙"}]
    r = build_select_config(name="theme", label="Theme", options=options)
    assert r["options"][0]["icon"] == "☀️"
