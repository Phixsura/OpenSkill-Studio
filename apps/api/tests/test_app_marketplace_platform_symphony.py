from app.services.app_marketplace_platform_symphony import get_symphony
def test_symphony():
    r = get_symphony()
    assert len(r["movements"]) == 4
    assert r["performances"] >= 4060
    assert "INFINITE" in r["encores"]
    assert "five stars" in r["critics"]
    assert "NEVER STOPS" in r["status"]
