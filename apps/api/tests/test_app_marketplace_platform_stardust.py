from app.services.app_marketplace_platform_stardust import get_stardust
def test_stardust():
    r = get_stardust()
    assert r["nucleosyntheses"] > 4000
    assert len(r["composition"]) == 4
    assert "cosmos" in r["sagan_quote"]
    assert r["entropy"].startswith("REVERSED")
    assert "NEVER STOPS" in r["status"]
