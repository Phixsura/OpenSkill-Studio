from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_readiness import fleet_readiness
def test_readiness():
    r = fleet_readiness([{"ready": True}, {"ready": False}, {"ready": True}])
    assert r["ready"] == 2
    assert r["not_ready"] == 1
    assert not r["all_ready"]
