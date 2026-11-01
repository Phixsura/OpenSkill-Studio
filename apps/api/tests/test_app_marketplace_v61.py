from app.services.app_marketplace_v61 import platform_v61
def test_v61():
    assert platform_v61()["version"] == "61.0"
