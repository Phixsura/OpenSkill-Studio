from app.services.app_marketplace_v70_big70 import platform_v70
def test_v70():
    assert platform_v70()["version"] == "70.0"
