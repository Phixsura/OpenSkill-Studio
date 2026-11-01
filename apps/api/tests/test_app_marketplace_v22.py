from app.services.app_marketplace_v22 import platform_v22
def test_v22():
    assert platform_v22()["version"] == "22.0"
    assert platform_v22()["lines"] > 310000
