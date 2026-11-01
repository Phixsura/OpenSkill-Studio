from app.services.app_marketplace_platform_glacier import get_glacier
def test_glacier():
    r = get_glacier()
    assert r["meltwater"].startswith("ZERO")
    assert len(r["moraines"]) == 3
    assert "never retreats" in r["ice_age"]
    assert "NEVER STOPS" in r["status"]
