from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_svc_disc import fleet_svc_discovery
def test_disc():
    r = fleet_svc_discovery([{"dns_resolvable": True}, {"dns_resolvable": False}, {"dns_resolvable": True, "dns_stale": True}])
    assert r["resolvable"] == 2
    assert r["stale_dns"] == 1
    assert not r["healthy"]
