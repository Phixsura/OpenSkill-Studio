from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_disk_io import fleet_disk_io
def test_io():
    r = fleet_disk_io([{"disk_read_mbps": 300, "disk_write_mbps": 200}, {"disk_read_mbps": 400, "disk_write_mbps": 200}])
    assert r["read_mbps"] == 700
    assert r["write_mbps"] == 400
    assert r["total_iops"] == 1100
    assert r["saturated"]
