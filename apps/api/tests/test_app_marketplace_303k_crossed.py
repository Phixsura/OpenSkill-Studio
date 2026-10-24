from app.services.app_marketplace_303k_crossed import celebrate_303k
def test_m():
    assert "303,000" in celebrate_303k()["milestone"]
