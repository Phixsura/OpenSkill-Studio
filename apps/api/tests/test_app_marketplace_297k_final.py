from app.services.app_marketplace_297k_final import celebrate_297k_final
def test_m():
    assert "297,000" in celebrate_297k_final()["milestone"]
