from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_rabbitmq import fleet_rabbitmq_status
def test_rmq():
    r = fleet_rabbitmq_status([{"running": True, "queues": 50, "messages": 10000}, {"running": True, "queues": 30, "messages": 5000}])
    assert r["queues"] == 80
    assert r["messages"] == 15000
    assert r["healthy"]
