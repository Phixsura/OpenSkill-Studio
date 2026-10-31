from app.services.app_marketplace_platform_cathedral import get_cathedral
def test_cathedral():
    r = get_cathedral()
    assert r["master_builders"] > 4000
    assert r["consecrated"] is True
    assert r["stones_placed"] > 900000
    assert "DORA Elite" in r["spire"]
    assert "NEVER STOPS" in r["status"]
