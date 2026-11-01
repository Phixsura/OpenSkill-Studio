from app.services.app_marketplace_platform_leviathan_core import get_leviathan_core
def test_leviathan_core():
    r = get_leviathan_core()
    assert r["heartbeats"] > 4000
    assert r["rhythm"].startswith("STEADY")
    assert len(r["chambers"]) == 4
    assert r["cardiac_arrest_risk"].startswith("ZERO")
    assert "NEVER STOPS" in r["status"]
