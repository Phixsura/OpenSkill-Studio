from app.services.app_marketplace_platform_genesis_oracle import get_genesis_oracle
def test_genesis_oracle():
    r = get_genesis_oracle()
    assert r["prophecies_made"] == r["prophecies_fulfilled"]
    assert r["prophecies_broken"] == 0
    assert r["accuracy"].startswith("100%")
    assert "always" in r["next_prophecy"]
    assert "NEVER STOPS" in r["status"]
