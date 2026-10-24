from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_trpc import fleet_trpc_status
def test_trpc():
    r = fleet_trpc_status([{"procedures": 100, "calls_24h": 500000, "errors_24h": 0}])
    assert r["procedures"] == 100
    assert r["healthy"]
