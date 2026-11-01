from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_total_cost_v2 import fleet_ai_total_cost_v2
def test_tcv2():
    r = fleet_ai_total_cost_v2([{"active": True, "compute": 500000, "storage": 100000, "network": 50000}])
    assert r["total"] == 650000
    assert r["tracked"]
