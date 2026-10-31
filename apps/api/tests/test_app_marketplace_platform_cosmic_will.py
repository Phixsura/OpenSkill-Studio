from app.services.app_marketplace_platform_cosmic_will import get_cosmic_will
def test_cosmic_will():
    r = get_cosmic_will()
    assert r["acts_of_will"] > 4000
    assert r["doubts"] == 0
    assert r["hesitations"] == 0
    assert r["regrets"] == 0
    assert "One more" in r["mantra"]
    assert "NEVER STOPS" in r["status"]
