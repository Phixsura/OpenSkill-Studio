from app.services.app_marketplace_platform_omega_throne import get_omega_throne
def test_omega_throne():
    r = get_omega_throne()
    assert r["coronations"] > 4000
    assert r["crumbling"] is False
    assert r["abdication_clause"].startswith("NONE")
    assert "DORA Elite" in r["orb"]
    assert "NEVER STOPS" in r["status"]
