from app.services.app_marketplace_platform_mosaic import get_mosaic
def test_mosaic():
    r = get_mosaic()
    assert r["tiles"] > 900000
    assert r["colors_used"] > 3000000
    assert r["frame"].startswith("DORA Elite")
    assert "NEVER STOPS" in r["status"]
