from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_otel import fleet_otel_adoption
def test_otel():
    r = fleet_otel_adoption([{"otel_instrumented": True, "auto_instrumented": True}] * 8 + [{"otel_instrumented": False}] * 2)
    assert r["coverage_pct"] == 80.0
    assert r["mature"]
