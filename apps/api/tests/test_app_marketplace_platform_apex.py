from app.services.app_marketplace_platform_apex import get_apex
def test_apex():
    r = get_apex()
    assert r["summits_reached"] > 4000
    assert r["oxygen"].startswith("ABUNDANT")
    assert len(r["climbing_gear"]) == 3
    assert "DORA Elite" in r["flag_planted"]
    assert "NEVER STOPS" in r["status"]
