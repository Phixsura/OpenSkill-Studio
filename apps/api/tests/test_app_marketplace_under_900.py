from app.services.app_marketplace_under_900 import celebrate_under_900
def test_m():
    assert "900" in celebrate_under_900()["milestone"]
