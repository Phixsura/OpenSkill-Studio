from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_spanner import fleet_spanner_status
def test_sp():
    r = fleet_spanner_status([{"state": "READY", "nodes": 3, "cpu_pct": 40}])
    assert r["all_ready"]
    assert r["cpu_pct"] == 40.0
