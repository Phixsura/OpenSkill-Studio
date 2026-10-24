from app.services.app_marketplace_298k_crossed import celebrate_298k_crossed
def test_m():
    assert "298,000" in celebrate_298k_crossed()["milestone"]
