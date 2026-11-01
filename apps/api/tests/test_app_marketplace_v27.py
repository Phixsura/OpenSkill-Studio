from app.services.app_marketplace_v27 import platform_v27
def test_v27():
    assert platform_v27()["version"] == "27.0"
