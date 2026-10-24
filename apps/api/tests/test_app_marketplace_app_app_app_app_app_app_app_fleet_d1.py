from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_d1 import fleet_d1_status
def test_d1():
    r = fleet_d1_status([{"active": True, "rows_read_24h": 10000000, "rows_written_24h": 500000}])
    assert r["rows_read_24h"] == 10000000
    assert r["all_active"]
