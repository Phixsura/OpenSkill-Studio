from app.services.app_marketplace_under_600 import celebrate_under_600
def test_m():
    assert "600" in celebrate_under_600()["milestone"]
