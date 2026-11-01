from app.services.app_marketplace_app_v14_summary import platform_v14_summary
def test_v14():
    r = platform_v14_summary()
    assert r["version"] == "14.0"
    assert r["dora"] == "Elite"
