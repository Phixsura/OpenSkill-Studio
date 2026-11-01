from app.services.app_marketplace_platform_cosmic_seed import get_cosmic_seed
def test_cosmic_seed():
    r = get_cosmic_seed()
    assert r["branches_of_reality"] > 4000
    assert r["still_growing"] is True
    assert r["harvest_date"].startswith("NEVER")
    assert "DORA Elite" in r["fruit"]
    assert "NEVER STOPS" in r["status"]
