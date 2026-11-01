from app.services.app_marketplace_under_400 import celebrate_under_400
def test_m():
    assert "400" in celebrate_under_400()["milestone"]
    assert celebrate_under_400()["remaining"] == 400
