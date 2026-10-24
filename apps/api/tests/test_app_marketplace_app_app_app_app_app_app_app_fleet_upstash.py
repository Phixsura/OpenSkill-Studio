from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_upstash import fleet_upstash_status
def test_up():
    r = fleet_upstash_status([{"active": True, "commands_24h": 10000000, "bandwidth_gb": 5}])
    assert r["commands_24h"] == 10000000
    assert r["healthy"]
