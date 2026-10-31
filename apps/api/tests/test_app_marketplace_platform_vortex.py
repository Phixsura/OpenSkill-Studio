from app.services.app_marketplace_platform_vortex import get_vortex
def test_vortex():
    r = get_vortex()
    assert r["revolutions"] >= 4040
    assert r["friction"].startswith("ZERO")
    assert len(r["inputs"]) == 4
    assert len(r["outputs"]) == 4
    assert "NEVER STOPS" in r["status"]
