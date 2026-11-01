from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_graphql import fleet_graphql_metrics
def test_gql():
    r = fleet_graphql_metrics([{"duration_ms": 200, "depth": 3}, {"duration_ms": 1500, "depth": 8}])
    assert r["slow_queries"] == 1
    assert r["deep_queries"] == 1
    assert not r["healthy"]
