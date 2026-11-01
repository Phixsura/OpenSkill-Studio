from app.services.app_marketplace_v16_final import platform_v16
def test_v16():
    r = platform_v16()
    assert r["version"] == "16.0"
    assert r["dora"] == "Elite"
