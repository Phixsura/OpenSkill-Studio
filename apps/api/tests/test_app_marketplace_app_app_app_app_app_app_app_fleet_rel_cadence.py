from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_rel_cadence import fleet_release_cadence
def test_cadence():
    r = fleet_release_cadence([{"day": 0}, {"day": 7}, {"day": 14}, {"day": 21}])
    assert r["avg_gap_days"] == 7.0
    assert r["regular"]
