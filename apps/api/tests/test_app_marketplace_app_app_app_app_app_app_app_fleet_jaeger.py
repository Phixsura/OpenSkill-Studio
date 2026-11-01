from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_jaeger import fleet_jaeger_status
def test_jaeger():
    r = fleet_jaeger_status([{"healthy": True, "spans_per_sec": 10000, "storage_gb": 200}])
    assert r["spans_per_sec"] == 10000
    assert r["all_healthy"]
