from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_extdns import fleet_extdns_status
def test_extdns():
    r = fleet_extdns_status([{"synced": True}, {"synced": True, "stale": True}])
    assert r["synced"] == 2
    assert r["stale"] == 1
    assert not r["healthy"]
