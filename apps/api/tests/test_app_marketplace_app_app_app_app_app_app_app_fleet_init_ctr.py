from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_init_ctr import fleet_init_containers
def test_init():
    r = fleet_init_containers([{"has_init_containers": True, "init_failed": False}, {"has_init_containers": True, "init_failed": True}])
    assert r["with_init"] == 2
    assert r["failed_init"] == 1
    assert not r["healthy"]
