from app.services.app_marketplace_v29 import platform_v29
def test_v29():
    assert platform_v29()["version"] == "29.0"
