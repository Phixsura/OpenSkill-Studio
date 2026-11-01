from app.services.app_marketplace_v68 import platform_v68
def test_v68():
    assert platform_v68()["version"] == "68.0"
