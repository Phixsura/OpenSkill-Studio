from app.services.app_marketplace_317k_crossed import celebrate_317k_crossed
def test_317kc():
    assert "317,000" in celebrate_317k_crossed()["milestone"]
