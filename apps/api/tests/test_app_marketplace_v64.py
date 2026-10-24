from app.services.app_marketplace_v64 import platform_v64
def test_v64():
    assert platform_v64()["version"] == "64.0"
