from app.services.app_marketplace_platform_ember import get_ember
def test_ember():
    r = get_ember()
    assert r["fires_extinguished"] == 0
    assert r["fires_lit"] > 4000
    assert r["ash"].startswith("ZERO")
    assert r["phoenix_potential"] == "MAXIMUM — every ember can birth a phoenix"
    assert "NEVER STOPS" in r["status"]
