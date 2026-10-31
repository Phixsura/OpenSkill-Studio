from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_usage_rpt import fleet_ai_usage_reporter
def test_ur():
    r = fleet_ai_usage_reporter([{"active": True, "reports_24h": 500, "recipients": 1000, "insights": 50}])
    assert r["reports_24h"] == 500
    assert r["informing"]
