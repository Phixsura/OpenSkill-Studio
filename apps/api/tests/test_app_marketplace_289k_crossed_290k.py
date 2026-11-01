from app.services.app_marketplace_289k_crossed_290k import celebrate_289k_crossed
def test_m():
    assert "289,000" in celebrate_289k_crossed()["milestone"]
