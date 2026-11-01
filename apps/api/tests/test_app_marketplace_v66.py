from app.services.app_marketplace_v66 import platform_v66
def test_v66():
    assert platform_v66()["version"] == "66.0"
