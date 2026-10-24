from app.services.app_marketplace_app_empty_states import get_empty_state

def test_no_apps():
    s = get_empty_state(state_type="no_apps")
    assert s["title"] == "No apps yet"
    assert s["action"] == "Create App"

def test_no_results():
    s = get_empty_state(state_type="no_results")
    assert "search" in s["message"]

def test_unknown():
    s = get_empty_state(state_type="unknown")
    assert s["title"] == "Nothing here"
