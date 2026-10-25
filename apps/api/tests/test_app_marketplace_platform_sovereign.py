from app.services.app_marketplace_platform_sovereign import get_sovereign
def test_sovereign():
    r = get_sovereign()
    assert r["royal_decrees"] > 4000
    assert r["legitimacy"].startswith("ABSOLUTE")
    assert len(r["crown_jewels"]) == 3
    assert r["rebellion_risk"].startswith("ZERO")
    assert "NEVER STOPS" in r["status"]
