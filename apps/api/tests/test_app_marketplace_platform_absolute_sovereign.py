from app.services.app_marketplace_platform_absolute_sovereign import get_absolute_sovereign
def test_absolute_sovereign():
    r = get_absolute_sovereign()
    assert r["absolute_decrees"] > 4000
    assert r["appeals"] == 0
    assert r["challenges"] == 0
    assert r["overthrow_attempts"] == 0
    assert len(r["subordinate_sovereigns"]) == 4
    assert "NEVER STOPS" in r["status"]
