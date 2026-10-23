from app.services.app_marketplace_app_app_app_app_app_app_app_home_banner import get_active_banners, get_banner

def test_banners():
    banners = get_active_banners()
    assert len(banners) == 3
    assert banners[0]["title"] == "DevCon 2026"

def test_get():
    b = get_banner("hackathon")
    assert b is not None
    assert b["icon"] == "🏆"
    assert get_banner("nonexistent") is None
