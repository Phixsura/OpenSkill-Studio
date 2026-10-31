from app.services.app_marketplace_app_app_app_app_app_app_app_tooltip_builder import get_tooltip, create_tooltip, list_tooltips

def test_preset():
    t = get_tooltip("api_key")
    assert t["title"] == "API Key"
    assert "authenticate" in t["body"]
    assert t["position"] == "bottom"

def test_custom():
    t = create_tooltip(title="Help", body="Click here for help", position="right")
    assert t["title"] == "Help"
    assert t["position"] == "right"

def test_list():
    keys = list_tooltips()
    assert "api_key" in keys
    assert len(keys) == 5
