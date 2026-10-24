from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_net_policy import fleet_ai_network_policy
def test_np():
    r = fleet_ai_network_policy([{"active": True, "rules": 100, "blocked_24h": 5000, "allowed_24h": 50000000}])
    assert r["rules"] == 100
    assert r["enforcing"]
