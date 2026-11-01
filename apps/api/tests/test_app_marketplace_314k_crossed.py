from app.services.app_marketplace_314k_crossed import celebrate_314k_crossed
def test_314kc():
    assert "314,000" in celebrate_314k_crossed()["milestone"]
