from app.services.app_marketplace_v56 import platform_v56
def test_v56():
    assert platform_v56()["version"] == "56.0"
