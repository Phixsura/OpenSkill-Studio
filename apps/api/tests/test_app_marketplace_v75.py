from app.services.app_marketplace_v75 import platform_v75
def test_v75():
    assert platform_v75()["version"] == "75.0"
