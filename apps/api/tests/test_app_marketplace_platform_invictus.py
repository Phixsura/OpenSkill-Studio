from app.services.app_marketplace_platform_invictus import get_invictus
def test_invictus():
    r = get_invictus()
    assert r["battles"] > 4000
    assert r["conquered"] is False
    assert r["bowed"] is False
    assert "masters" in r["soul_captain"]
    assert "NEVER STOPS" in r["status"]
