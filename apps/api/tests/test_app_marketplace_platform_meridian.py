from app.services.app_marketplace_platform_meridian import get_meridian
def test_meridian():
    r = get_meridian()
    assert all(v == 0 for v in r["zero_definitions"].values())
    assert r["alignment"].startswith("PERFECT")
    assert r["precision_degrees"] > 4000
    assert "NEVER STOPS" in r["status"]
