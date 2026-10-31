from app.services.app_marketplace_platform_cosmos import get_cosmos
def test_cosmos():
    r = get_cosmos()
    assert r["cosmic_events"] > 4000
    assert r["entropy"].startswith("ZERO")
    assert len(r["galaxies"]) == 3
    assert "NEVER" in r["heat_death"]
    assert "NEVER STOPS" in r["status"]
