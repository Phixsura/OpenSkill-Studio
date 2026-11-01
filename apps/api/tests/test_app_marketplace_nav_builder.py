from app.services.app_marketplace_nav_builder import build_nav_state

def test_valid():
    s = build_nav_state("home")
    assert s["is_valid"] is True
    assert s["active"] == "home"

def test_invalid():
    s = build_nav_state("nonexist")
    assert s["is_valid"] is False
