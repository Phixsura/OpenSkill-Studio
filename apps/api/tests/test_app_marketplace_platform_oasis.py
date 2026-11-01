from app.services.app_marketplace_platform_oasis import get_oasis
def test_oasis():
    r = get_oasis()
    assert r["mirage"] is False
    assert r["real"] is True
    assert r["springs"] > 4000
    assert r["shade_coverage"] == "100% — no developer left in the sun"
    assert "NEVER STOPS" in r["status"]
