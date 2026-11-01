from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_graphql_gateway_v9 import fleet_graphql_gateway_v9
def test_gql_v9():
    r = fleet_graphql_gateway_v9([{"queries_per_sec": 5000, "mutations_per_sec": 500, "cache_hit_pct": 85}])
    assert r["qps"] == 5000
    assert r["healthy"]
