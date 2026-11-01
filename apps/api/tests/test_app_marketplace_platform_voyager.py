from app.services.app_marketplace_platform_voyager import get_voyager
def test_voyager():
    r = get_voyager()
    assert r["interstellar"] is True
    assert r["golden_record"]["test_failures"] == 0
    assert r["signal_strength"].startswith("STRONG")
    assert r["mission_status"].startswith("ONGOING")
    assert "NEVER STOPS" in r["status"]
