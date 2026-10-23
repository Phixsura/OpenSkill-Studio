from app.services.app_marketplace_app_app_app_app_app_app_app_empty_states import get_empty_state, list_sections

def test_empty_state():
    s = get_empty_state("apps")
    assert s["title"] == "No apps yet"
    assert s["cta"] == "Create App"
    assert s["icon"] == "📱"

def test_unknown():
    s = get_empty_state("unknown")
    assert s["title"] == "Nothing here"

def test_sections():
    assert "apps" in list_sections()
    assert "webhooks" in list_sections()
    assert len(list_sections()) == 7
