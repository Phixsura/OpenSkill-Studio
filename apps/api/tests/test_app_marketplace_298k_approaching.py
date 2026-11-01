from app.services.app_marketplace_298k_approaching import celebrate_298k
def test_m():
    assert "298,000" in celebrate_298k()["milestone"]
