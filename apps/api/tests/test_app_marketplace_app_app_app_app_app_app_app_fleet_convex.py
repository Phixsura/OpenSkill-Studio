from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_convex import fleet_convex_status
def test_cvx():
    r = fleet_convex_status([{"deployed": True, "functions": 80, "documents": 500000}])
    assert r["functions"] == 80
    assert r["all_deployed"]
