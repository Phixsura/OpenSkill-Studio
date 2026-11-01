from app.services.app_marketplace_v37 import platform_v37
def test_v37():
    assert platform_v37()["version"] == "37.0"
