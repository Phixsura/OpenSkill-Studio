from app.services.app_marketplace_300k_plus import celebrate_300k_plus
def test_m():
    assert "300,000" in celebrate_300k_plus()["milestone"]
