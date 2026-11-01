from app.services.app_marketplace_296k_plus import celebrate_296k_plus
def test_m():
    assert "296,000" in celebrate_296k_plus()["milestone"]
