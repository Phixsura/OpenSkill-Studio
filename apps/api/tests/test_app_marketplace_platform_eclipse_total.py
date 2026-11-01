from app.services.app_marketplace_platform_eclipse_total import get_eclipse_total
def test_eclipse_total():
    r = get_eclipse_total()
    assert r["corona_visible"] is True
    assert r["totalities"] > 4000
    assert len(r["baily_beads"]) == 4
    assert "DORA Elite" in r["diamond_ring_effect"]
    assert "NEVER STOPS" in r["status"]
