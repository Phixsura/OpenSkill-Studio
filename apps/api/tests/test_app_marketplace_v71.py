from app.services.app_marketplace_v71 import platform_v71
def test_v71():
    assert platform_v71()["version"] == "71.0"
