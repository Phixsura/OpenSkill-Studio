from app.services.app_marketplace_under_700 import celebrate_under_700
def test_m():
    assert "700" in celebrate_under_700()["milestone"]
