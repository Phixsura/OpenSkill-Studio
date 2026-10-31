from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_19k_files_official import fleet_19k_files_official
def test_19k_off():
    r = fleet_19k_files_official()
    assert "19,000" in r["milestone"]
    assert r["files"] >= 19000
