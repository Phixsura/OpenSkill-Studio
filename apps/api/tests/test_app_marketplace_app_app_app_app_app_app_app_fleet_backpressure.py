from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_backpressure import fleet_backpressure
def test_bp():
    r = fleet_backpressure([{"backpressure_active": True, "dropped_messages": 100}, {"backpressure_active": False, "dropped_messages": 0}])
    assert r["pressured"] == 1
    assert r["dropped"] == 100
    assert not r["stable"]
