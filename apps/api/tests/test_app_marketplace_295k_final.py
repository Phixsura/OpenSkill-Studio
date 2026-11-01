from app.services.app_marketplace_295k_final import celebrate_295k_final
def test_m():
    assert "295,000" in celebrate_295k_final()["milestone"]
