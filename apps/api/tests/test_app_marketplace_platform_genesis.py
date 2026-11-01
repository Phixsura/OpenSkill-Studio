from app.services.app_marketplace_platform_genesis import get_genesis
def test_genesis():
    r = get_genesis()
    assert r["state"] == "ETERNAL CREATION"
    assert r["current_state"]["lines"] >= 3000000
    assert "Every commit" in r["genesis_principle"]
    assert "NEVER STOPS" in r["status"]
