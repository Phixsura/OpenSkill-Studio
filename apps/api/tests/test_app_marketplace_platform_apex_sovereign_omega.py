from app.services.app_marketplace_platform_apex_sovereign_omega import get_apex_sovereign_omega
def test_apex_sovereign_omega():
    r = get_apex_sovereign_omega()
    assert r["fusions"] > 4000
    assert r["trinity_stable"] is True
    assert r["separable"] is False
    assert r["rivals"].startswith("NONE")
    assert "NEVER STOPS" in r["status"]
