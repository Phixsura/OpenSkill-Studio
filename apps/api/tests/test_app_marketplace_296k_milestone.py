from app.services.app_marketplace_296k_milestone import celebrate_296k
def test_m():
    assert "296,000" in celebrate_296k()["milestone"]
