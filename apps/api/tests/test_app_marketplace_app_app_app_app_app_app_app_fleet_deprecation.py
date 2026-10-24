from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_deprecation import fleet_deprecation_tracker
def test_deprecation():
    r = fleet_deprecation_tracker([{"deprecated": True, "requests_24h": 100}, {"deprecated": True, "requests_24h": 0}, {"deprecated": False}])
    assert r["deprecated"] == 2
    assert r["still_used"] == 1
    assert r["safe_to_remove"] == 1
