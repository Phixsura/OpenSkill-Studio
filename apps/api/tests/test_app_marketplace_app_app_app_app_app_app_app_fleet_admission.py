from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_admission import fleet_admission_stats
def test_admission():
    r = fleet_admission_stats([{"calls": 1000, "denied": 50, "errors": 0}, {"calls": 500, "denied": 10, "errors": 2}])
    assert r["denied"] == 60
    assert r["errors"] == 2
    assert not r["healthy"]
