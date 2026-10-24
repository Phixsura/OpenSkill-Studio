from app.services.app_marketplace_v79 import platform_v79
def test_v79():
    assert platform_v79()["version"] == "79.0"
