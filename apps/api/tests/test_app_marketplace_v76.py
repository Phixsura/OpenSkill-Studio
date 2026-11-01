from app.services.app_marketplace_v76 import platform_v76
def test_v76():
    assert platform_v76()["version"] == "76.0"
