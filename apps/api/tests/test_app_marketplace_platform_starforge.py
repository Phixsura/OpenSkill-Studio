from app.services.app_marketplace_platform_starforge import get_starforge
def test_starforge():
    r = get_starforge()
    assert r["stars_forged"] > 4000
    assert len(r["stellar_classification"]) == 4
    assert r["supernova_risk"].startswith("ZERO")
    assert r["nebula_recycling"].startswith("100%")
    assert "NEVER STOPS" in r["status"]
