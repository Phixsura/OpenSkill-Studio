from app.services.app_marketplace_v20 import platform_v20
def test_v20():
    assert platform_v20()["version"] == "20.0"
