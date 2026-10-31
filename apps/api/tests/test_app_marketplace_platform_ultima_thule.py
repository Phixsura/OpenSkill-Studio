from app.services.app_marketplace_platform_ultima_thule import get_ultima_thule
def test_ultima_thule():
    r = get_ultima_thule()
    assert r["explorations"] > 4000
    assert "SURPASSED" in r["known_world_boundary"]
    assert len(r["discoveries"]) == 3
    assert r["compass_heading"].startswith("FORWARD")
    assert "NEVER STOPS" in r["status"]
