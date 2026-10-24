from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_rbac import fleet_ai_rbac
def test_rbac():
    r = fleet_ai_rbac([{"active": True, "roles": 50, "policies": 200, "evals_24h": 100000000}])
    assert r["roles"] == 50
    assert r["enforcing"]
