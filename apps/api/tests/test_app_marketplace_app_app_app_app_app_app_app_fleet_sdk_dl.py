from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sdk_dl import fleet_sdk_downloads
def test_dl():
    r = fleet_sdk_downloads([{"language": "Python", "downloads": 50000}, {"language": "TypeScript", "downloads": 80000}])
    assert r["total_downloads"] == 130000
    assert r["top_sdk"] == "TypeScript"
