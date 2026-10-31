from app.services.app_marketplace_platform_multiverse_key import get_multiverse_key
def test_multiverse_key():
    r = get_multiverse_key()
    assert r["doors_opened"] > 4000
    assert r["doors_locked"] == 0
    assert r["master_key"] is True
    assert r["original"] is True
    assert "NEVER STOPS" in r["status"]
