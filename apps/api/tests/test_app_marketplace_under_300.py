from app.services.app_marketplace_under_300 import celebrate_under_300
def test_m():
    assert "300" in celebrate_under_300()["milestone"]
    assert celebrate_under_300()["remaining"] == 300
