from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_nx import fleet_nx_status
def test_nx():
    r = fleet_nx_status([{"affected": True, "from_cache": True, "build_sec": 5}] * 6 + [{"affected": False, "from_cache": False, "build_sec": 30}] * 4)
    assert r["affected"] == 6
    assert r["from_cache"] == 6
    assert r["efficient"]
