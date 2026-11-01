from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_secret_scan import fleet_secret_scan
def test_scan():
    r = fleet_secret_scan([{"secrets_found": 0}, {"secrets_found": 3}])
    assert r["leaked"] == 3
    assert not r["all_clean"]
