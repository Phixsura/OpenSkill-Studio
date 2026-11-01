from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_opentelemetry_v9 import fleet_api_opentelemetry_v9
def test_aotel_v9():
    r = fleet_api_opentelemetry_v9([{"otel_enabled": True, "traces_per_sec": 10000, "metrics_per_sec": 50000}])
    assert r["instrumented"] == 1
    assert r["healthy"]
