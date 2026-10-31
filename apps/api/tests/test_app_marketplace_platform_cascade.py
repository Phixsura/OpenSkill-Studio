from app.services.app_marketplace_platform_cascade import get_cascade
def test_cascade():
    r = get_cascade()
    assert r["waterfalls"] > 4000
    assert len(r["levels"]) == 4
    assert r["turbulence"].startswith("ZERO")
    assert r["evaporation"] == "NONE — nothing is lost"
    assert "NEVER STOPS" in r["status"]
