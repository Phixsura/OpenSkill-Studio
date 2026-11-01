from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_grafbase import fleet_grafbase_status
def test_gb():
    r = fleet_grafbase_status([{"deployed": True, "resolvers": 100, "requests_24h": 2000000}])
    assert r["resolvers"] == 100
    assert r["all_deployed"]
