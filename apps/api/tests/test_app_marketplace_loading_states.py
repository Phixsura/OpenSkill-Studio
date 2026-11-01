from app.services.app_marketplace_loading_states import build_loading_state, get_error_state, get_empty_state_for_component

def test_loading():
    s = build_loading_state(component="app_card", item_count=5)
    assert s["count"] == 5
    assert len(s["items"]) == 5
    assert s["animation"] == "pulse"

def test_unknown_component():
    s = build_loading_state(component="unknown")
    assert s["skeleton"]["elements"] == ["content"]

def test_error():
    e = get_error_state(component="app_list", error="Network error")
    assert e["retryable"]
    assert e["action"] == "Retry"

def test_error_not_retryable():
    e = get_error_state(component="x", error="Forbidden", retryable=False)
    assert e["action"] == "Go Back"

def test_empty():
    e = get_empty_state_for_component(component="reviews")
    assert e["icon"] == "⭐"
    assert "first" in e["message"]
