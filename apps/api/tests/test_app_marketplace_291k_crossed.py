from app.services.app_marketplace_291k_crossed import celebrate_291k_crossed
def test_m():
    assert "291,000" in celebrate_291k_crossed()["milestone"]
