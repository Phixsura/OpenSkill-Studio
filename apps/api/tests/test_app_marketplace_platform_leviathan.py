from app.services.app_marketplace_platform_leviathan import get_leviathan
def test_leviathan():
    r = get_leviathan()
    assert r["cells"] > 900000
    assert r["predators"] == "NONE — apex of the ecosystem"
    assert r["heartbeats"] > 4000
    assert "THRIVING" in r["conservation_status"]
    assert "NEVER STOPS" in r["status"]
