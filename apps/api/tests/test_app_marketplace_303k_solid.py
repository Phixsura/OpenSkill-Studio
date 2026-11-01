from app.services.app_marketplace_303k_solid import celebrate_303k_solid
def test_m():
    assert "303,000" in celebrate_303k_solid()["milestone"]
