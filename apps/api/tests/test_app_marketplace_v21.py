from app.services.app_marketplace_v21 import platform_v21
def test_v21():
    assert platform_v21()["version"] == "21.0"
