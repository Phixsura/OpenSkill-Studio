from app.services.app_marketplace_321k_crossed import celebrate_321k_crossed
def test_321kc():
    assert "321,000" in celebrate_321k_crossed()["milestone"]
