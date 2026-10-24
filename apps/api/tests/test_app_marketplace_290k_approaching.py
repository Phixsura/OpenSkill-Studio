from app.services.app_marketplace_290k_approaching import celebrate_290k_approaching
def test_m():
    assert "290,000" in celebrate_290k_approaching()["milestone"]
