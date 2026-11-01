from app.services.app_marketplace_310k_crossed import celebrate_310k_crossed
def test_310kc():
    assert "310,000" in celebrate_310k_crossed()["milestone"]
