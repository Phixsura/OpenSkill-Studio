from app.services.app_marketplace_296k_crossed import celebrate_296k_crossed
def test_m():
    assert "296,000" in celebrate_296k_crossed()["milestone"]
