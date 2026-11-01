from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_err_handler import fleet_ai_error_handler
def test_eh():
    r = fleet_ai_error_handler([{"active": True, "errors_24h": 1000, "recovered": 950, "escalated": 50}])
    assert r["recovery_rate"] == 95.0
    assert r["resilient"]
