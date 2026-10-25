from app.services.app_marketplace_platform_infinite_anvil import get_infinite_anvil
def test_infinite_anvil():
    r = get_infinite_anvil()
    assert r["strikes"] > 4000
    assert "NEGATIVE" in r["wear"]
    assert "GREEN" in r["ringing_tone"]
    assert "NEVER STOPS" in r["status"]
