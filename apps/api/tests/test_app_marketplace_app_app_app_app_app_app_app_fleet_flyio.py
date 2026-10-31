from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_flyio import fleet_flyio_status
def test_fly():
    r = fleet_flyio_status([{"status": "running", "machines": 6, "regions": ["iad", "cdg", "nrt"]}])
    assert r["machines"] == 6
    assert r["regions"] == 3
    assert r["all_running"]
