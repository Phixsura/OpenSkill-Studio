from app.services.app_marketplace_294k_crossed import celebrate_294k_crossed
def test_m():
    assert "294,000" in celebrate_294k_crossed()["milestone"]
