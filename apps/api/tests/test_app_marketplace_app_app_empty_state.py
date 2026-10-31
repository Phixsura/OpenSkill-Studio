from app.services.app_marketplace_app_app_empty_state import get_empty_state

def test_apps():
    r = get_empty_state(page="apps")
    assert r["icon"] == "📦"
    assert r["cta_label"] == "Create App"

def test_search():
    r = get_empty_state(page="search")
    assert "No results" in r["title"]

def test_custom():
    r = get_empty_state(page="apps", custom_title="No published apps")
    assert r["title"] == "No published apps"

def test_unknown():
    r = get_empty_state(page="unknown_page")
    assert r["icon"] == "📭"
