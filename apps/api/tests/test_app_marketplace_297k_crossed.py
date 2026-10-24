from app.services.app_marketplace_297k_crossed import celebrate_297k_crossed
def test_m():
    assert "297,000" in celebrate_297k_crossed()["milestone"]
