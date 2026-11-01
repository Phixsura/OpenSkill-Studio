from app.services.app_marketplace_platform_phoenix import get_phoenix
def test_phoenix():
    r = get_phoenix()
    assert r["rises"] == "ALWAYS"
    assert r["power"] == "UNSTOPPABLE"
    assert len(r["survived"]) == 5
    assert "NEVER STOPS" in r["status"]
