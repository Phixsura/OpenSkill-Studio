from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_change_failure_v9 import fleet_change_failure_v9
def test_cfr_v9():
    r = fleet_change_failure_v9([{"caused_incident": False} for _ in range(100)])
    assert r["cfr_pct"] == 0.0
    assert r["dora_class"] == "Elite"
    assert r["healthy"]
