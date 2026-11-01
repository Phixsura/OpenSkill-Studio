from app.services.app_marketplace_tooltip import get_tooltip, get_all_tooltips

def test_get():
    t = get_tooltip(key="install_count")
    assert t is not None
    assert "installed" in t["text"]
    assert t["learn_more"].startswith("/docs")

def test_unknown():
    assert get_tooltip(key="nonexistent") is None

def test_all():
    t = get_all_tooltips()
    assert len(t) >= 8
    assert "uptime" in t
