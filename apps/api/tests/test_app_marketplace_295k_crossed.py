from app.services.app_marketplace_295k_crossed import celebrate_295k_crossed
def test_m():
    assert "295,000" in celebrate_295k_crossed()["milestone"]
