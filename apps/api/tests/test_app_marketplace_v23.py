from app.services.app_marketplace_v23 import platform_v23
def test_v23():
    assert platform_v23()["version"] == "23.0"
