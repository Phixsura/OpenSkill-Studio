from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_exec_dash_v6 import fleet_ai_exec_dashboard_v6
def test_edv6():
    r = fleet_ai_exec_dashboard_v6([{"active": True, "revenue_usd": 500000000, "cost_usd": 150000000, "users": 10000000}])
    assert r["margin"] == 70.0
    assert r["profitable"]
