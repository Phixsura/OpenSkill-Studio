from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_nginx import fleet_nginx_status
def test_nginx():
    r = fleet_nginx_status([{"active_connections": 5000, "rps": 10000, "errors_5xx": 5}])
    assert r["rps"] == 10000
    assert r["errors_5xx"] == 5
    assert not r["healthy"]
