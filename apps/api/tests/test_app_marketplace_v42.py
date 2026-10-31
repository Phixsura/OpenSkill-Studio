from app.services.app_marketplace_v42 import platform_v42
def test_v42():
    assert platform_v42()["version"] == "42.0"
