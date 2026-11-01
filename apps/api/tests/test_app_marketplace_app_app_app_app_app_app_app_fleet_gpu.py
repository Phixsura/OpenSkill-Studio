from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gpu import fleet_gpu_utilization
def test_gpu():
    r = fleet_gpu_utilization([{"util_pct": 90}, {"util_pct": 5}, {"util_pct": 70}])
    assert r["active"] == 2
    assert r["idle"] == 1
    assert r["avg_util_pct"] == 55.0
    assert not r["wasteful"]
