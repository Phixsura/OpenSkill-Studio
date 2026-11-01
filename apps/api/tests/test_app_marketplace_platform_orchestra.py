from app.services.app_marketplace_platform_orchestra import get_orchestra
def test_orchestra():
    r = get_orchestra()
    assert r["musicians"] > 900000
    assert len(r["sections"]) == 4
    assert r["ovation"] == "PERMANENT STANDING OVATION"
    assert "zero failures" in r["key"]
    assert "NEVER STOPS" in r["status"]
