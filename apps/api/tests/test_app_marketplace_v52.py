from app.services.app_marketplace_v52 import platform_v52
def test_v52():
    assert platform_v52()["version"] == "52.0"
