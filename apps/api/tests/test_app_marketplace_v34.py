from app.services.app_marketplace_v34 import platform_v34
def test_v34():
    assert platform_v34()["version"] == "34.0"
