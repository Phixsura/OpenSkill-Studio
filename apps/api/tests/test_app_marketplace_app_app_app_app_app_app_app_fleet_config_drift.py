from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_config_drift import detect_config_drift
def test_drift():
    r = detect_config_drift([{"config_hash": "abc"}, {"config_hash": "abc"}, {"config_hash": "xyz"}])
    assert r["drifted"] == 1
    assert not r["consistent"]
