from app.services.app_marketplace_v24 import platform_v24
def test_v24():
    assert platform_v24()["version"] == "24.0"
    assert platform_v24()["commits"] == 3600
