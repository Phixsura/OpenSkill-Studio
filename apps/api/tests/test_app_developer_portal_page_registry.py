from app.services.app_developer_portal_page_registry import get_page, get_all_pages

def test_get():
    p = get_page("apps")
    assert p is not None
    assert p["title"] == "My Apps"

def test_get_unknown():
    assert get_page("nonexist") is None

def test_all():
    assert len(get_all_pages()) >= 7
