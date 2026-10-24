from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_rbac_v5 import fleet_ai_rbac_v5
def test_rv5():
    r = fleet_ai_rbac_v5([{"active": True, "roles": 200, "permissions": 2000, "evals": 1000000000}])
    assert r["roles"] == 200
    assert r["enforcing"]
