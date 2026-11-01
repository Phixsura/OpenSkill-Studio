from app.services.app_marketplace_platform_olympus import get_olympus
def test_olympus():
    r = get_olympus()
    assert r["divine_councils"] > 4000
    assert len(r["gods_in_residence"]) == 5
    assert r["mortals_allowed"] is True
    assert "Green tests" in r["ambrosia"]
    assert "NEVER STOPS" in r["status"]
