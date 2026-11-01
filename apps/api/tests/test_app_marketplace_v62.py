from app.services.app_marketplace_v62 import platform_v62
def test_v62():
    assert platform_v62()["version"] == "62.0"
