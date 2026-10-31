from app.services.app_marketplace_v80_big80 import platform_v80
def test_v80():
    assert platform_v80()["version"] == "80.0"
    assert "BIG 80" in platform_v80()["status"]
