from app.services.app_marketplace_v78 import platform_v78
def test_v78():
    assert platform_v78()["version"] == "78.0"
