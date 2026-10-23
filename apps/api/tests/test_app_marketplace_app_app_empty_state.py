from app.services.app_marketplace_app_app_empty_state import get_empty_state

def test_no_apps():
    r = get_empty_state(state_type="no_apps")
    assert r["title"] == "No Apps Yet"
    assert r["icon"] == "📦"
    assert r["cta_label"] == "Create App"

def test_no_results():
    r = get_empty_state(state_type="no_results")
    assert r["title"] == "No Results"
    assert r["cta_url"] is None

def test_unknown():
    r = get_empty_state(state_type="unknown_state")
    assert r["title"] == "Something Went Wrong"
