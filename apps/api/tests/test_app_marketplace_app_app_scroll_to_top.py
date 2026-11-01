from app.services.app_marketplace_app_app_scroll_to_top import get_scroll_config

def test_default():
    r = get_scroll_config()
    assert r["show_threshold"] == 300
    assert r["smooth"]
    assert "bottom-6 right-6" in r["position_class"]

def test_custom():
    r = get_scroll_config(show_threshold=500, smooth=False, position="bottom-left")
    assert r["scroll_behavior"] == "auto"
    assert "left-6" in r["position_class"]
