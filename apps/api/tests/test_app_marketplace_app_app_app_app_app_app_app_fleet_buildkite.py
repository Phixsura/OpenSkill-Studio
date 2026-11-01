from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_buildkite import fleet_buildkite_status
def test_bk():
    r = fleet_buildkite_status([{"passing": True, "agents": 10, "avg_queue_sec": 15}])
    assert r["agents"] == 10
    assert r["fast_queue"]
