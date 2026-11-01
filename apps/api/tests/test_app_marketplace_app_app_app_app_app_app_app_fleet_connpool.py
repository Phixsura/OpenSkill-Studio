from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_connpool import fleet_connpool
def test_connpool():
    r = fleet_connpool([{"conns_used": 40, "conns_max": 50}, {"conns_used": 45, "conns_max": 50}])
    assert r["used"] == 85
    assert r["pct"] == 85.0
    assert not r["saturated"]  # 85.0 is not > 85
