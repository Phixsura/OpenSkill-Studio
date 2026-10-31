from app.services.app_marketplace_v81 import platform_v81
def test_v81():
    assert platform_v81()["version"] == "81.0"
