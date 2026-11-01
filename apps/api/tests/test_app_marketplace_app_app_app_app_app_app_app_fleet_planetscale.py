from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_planetscale import fleet_planetscale_status
def test_ps():
    r = fleet_planetscale_status([{"branch": "main", "deploy_requests_open": 2, "rows_read_24h": 50000000}])
    assert r["production"] == 1
    assert r["rows_read_24h"] == 50000000
