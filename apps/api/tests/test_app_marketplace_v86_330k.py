from app.services.app_marketplace_v86_330k import platform_v86
def test_v86():
    assert platform_v86()["version"] == "86.0"
    assert platform_v86()["lines"] >= 330000
