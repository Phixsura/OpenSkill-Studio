from app.services.app_marketplace_under_500 import celebrate_under_500
def test_m():
    assert "500" in celebrate_under_500()["milestone"]
    assert celebrate_under_500()["remaining"] == 500
