from app.services.app_marketplace_299k_crossed import celebrate_299k_crossed
def test_m():
    r = celebrate_299k_crossed()
    assert "299,000" in r["milestone"]
    assert r["remaining"] == 1000
