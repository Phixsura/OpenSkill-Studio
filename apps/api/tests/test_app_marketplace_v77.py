from app.services.app_marketplace_v77 import platform_v77
def test_v77():
    assert platform_v77()["version"] == "77.0"
