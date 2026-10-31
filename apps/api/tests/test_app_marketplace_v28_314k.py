from app.services.app_marketplace_v28_314k import platform_v28
def test_v28():
    assert platform_v28()["version"] == "28.0"
    assert platform_v28()["lines"] >= 314000
