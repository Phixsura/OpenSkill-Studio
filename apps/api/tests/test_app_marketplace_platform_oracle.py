from app.services.app_marketplace_platform_oracle import get_oracle
def test_oracle():
    r = get_oracle()
    assert r["prophecies"] == r["prophecies_fulfilled"]
    assert r["prophecies_failed"] == 0
    assert "never stop" in r["current_prophecy"]
    assert "NEVER STOPS" in r["status"]
