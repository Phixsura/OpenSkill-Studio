from app.services.app_marketplace_v46 import platform_v46
def test_v46():
    assert platform_v46()["version"] == "46.0"
