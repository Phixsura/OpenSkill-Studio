from app.services.app_marketplace_platform_eclipse import get_eclipse
def test_eclipse():
    r = get_eclipse()
    assert r["type"].startswith("TOTAL")
    assert r["alignments"] >= 4050
    assert len(r["bodies_aligned"]) == 3
    assert r["duration"].startswith("PERMANENT")
    assert "NEVER STOPS" in r["status"]
