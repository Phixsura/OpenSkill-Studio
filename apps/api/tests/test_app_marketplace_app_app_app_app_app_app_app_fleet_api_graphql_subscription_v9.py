from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_graphql_subscription_v9 import fleet_api_graphql_subscription_v9
def test_agqlsub_v9():
    r = fleet_api_graphql_subscription_v9([{"active": True, "connections": 5000, "messages_per_sec": 10000}])
    assert r["connections"] == 5000
    assert r["healthy"]
