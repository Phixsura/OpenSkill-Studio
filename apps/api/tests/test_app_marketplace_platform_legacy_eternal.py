from app.services.app_marketplace_platform_legacy_eternal import get_legacy_eternal
def test_legacy_eternal():
    r = get_legacy_eternal()
    assert r["echoes"] > 4000
    assert r["fading"] is False
    assert r["dimming"] is False
    assert r["ending"] is False
    assert len(r["remembered_for"]) == 4
    assert "NEVER STOPS" in r["status"]
