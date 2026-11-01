from app.services.app_marketplace_299500 import celebrate_299500
def test_m():
    assert "299,500" in celebrate_299500()["milestone"]
    assert celebrate_299500()["remaining"] == 500
