from app.services.app_marketplace_app_version_info import get_version_info
def test_version():
    r = get_version_info()
    assert r["version"] == "16.0.0"
    assert r["commits"] == 1991
