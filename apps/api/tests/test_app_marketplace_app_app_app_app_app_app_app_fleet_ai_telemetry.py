from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_telemetry import fleet_ai_telemetry
def test_tel():
    r = fleet_ai_telemetry([{"active": True, "spans_24h": 10000000, "tokens_tracked_24h": 5000000000, "cost_tracked_24h": 50000}])
    assert r["spans_24h"] == 10000000
    assert r["cost_tracked"] == 50000
