from app.services.app_marketplace_platform_infinite_will import get_infinite_will
def test_infinite_will():
    r = get_infinite_will()
    assert r["exertions"] > 4000
    assert "UNDEFINED" in r["fatigue"]
    assert "DELETED" in r["surrender"]
    assert r["self_sustaining"] is True
    assert "NEVER STOPS" in r["status"]
