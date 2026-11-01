from app.services.app_marketplace_under_800 import celebrate_under_800
def test_m():
    assert "800" in celebrate_under_800()["milestone"]
