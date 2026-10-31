from app.services.app_marketplace_336k_crossed import celebrate_336k_crossed
def test_336k_crossed():
    assert "336,000" in celebrate_336k_crossed()["milestone"]
