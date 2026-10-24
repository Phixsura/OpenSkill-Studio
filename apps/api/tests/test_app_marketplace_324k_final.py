from app.services.app_marketplace_324k_final import celebrate_324k_final
def test_324kf():
    assert "324,000" in celebrate_324k_final()["milestone"]
