from app.services.app_marketplace_under_200 import celebrate_under_200
def test_m():
    assert "200" in celebrate_under_200()["milestone"]
    assert celebrate_under_200()["remaining"] == 200
