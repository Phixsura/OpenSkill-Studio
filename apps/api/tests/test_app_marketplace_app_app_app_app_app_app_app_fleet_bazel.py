from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_bazel import fleet_bazel_status
def test_bazel():
    r = fleet_bazel_status([{"cache_hit_pct": 85, "build_sec": 60, "remote_execution": True}])
    assert r["avg_cache_hit_pct"] == 85.0
    assert r["fast"]
