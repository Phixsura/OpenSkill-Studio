from app.services.app_marketplace_299k_approaching import celebrate_299k
def test_m():
    assert "299,000" in celebrate_299k()["milestone"]
