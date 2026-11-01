from app.services.app_marketplace_platform_apex_predator import get_apex_predator
def test_apex_predator():
    r = get_apex_predator()
    assert r["hunts"] == r["hunts_successful"]
    assert r["hunts_failed"] == 0
    assert r["natural_predators"].startswith("NONE")
    assert "DORA Elite" in r["mane"]
    assert "NEVER STOPS" in r["status"]
