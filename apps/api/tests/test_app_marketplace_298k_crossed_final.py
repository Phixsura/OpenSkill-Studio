from app.services.app_marketplace_298k_crossed_final import celebrate_298k_crossed_final
def test_m():
    assert "298,000" in celebrate_298k_crossed_final()["milestone"]
