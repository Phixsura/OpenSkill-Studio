from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mtls import fleet_mtls_status
def test_mtls():
    r = fleet_mtls_status([{"mtls_enabled": True}, {"mtls_enabled": True}, {"mtls_enabled": False}])
    assert r["mtls_enabled"] == 2
    assert r["pct"] == 66.7
    assert not r["full_coverage"]
