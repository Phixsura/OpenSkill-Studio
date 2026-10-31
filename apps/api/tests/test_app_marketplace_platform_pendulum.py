from app.services.app_marketplace_platform_pendulum import get_pendulum
def test_pendulum():
    r = get_pendulum()
    assert r["oscillations"] > 4000
    assert r["friction"].startswith("ZERO")
    assert r["period"].startswith("CONSTANT")
    assert len(r["energy"]) == 2
    assert "NEVER STOPS" in r["status"]
