from app.services.app_marketplace_platform_adamantine import get_adamantine
def test_adamantine():
    r = get_adamantine()
    assert r["break_successes"] == 0
    assert r["break_attempts"] > 4000
    assert all(r["properties"].values())
    assert len(r["properties"]) == 4
    assert "NEVER STOPS" in r["status"]
