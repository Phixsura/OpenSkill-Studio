from app.services.app_marketplace_platform_3015k_lines import get_3015k_lines
def test_3015k():
    r = get_3015k_lines()
    assert r["commits"] > 4000
    assert r["army_morale"] == "MAXIMUM — unbreakable spirit"
    assert "UNKNOWN" in r["retreat"]
    assert "DORA Elite" in r["general"]
    assert "NEVER STOPS" in r["status"]
