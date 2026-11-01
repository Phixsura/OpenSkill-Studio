from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dlq import fleet_dlq_status
def test_dlq():
    r = fleet_dlq_status([{"messages": 0}, {"messages": 50}, {"messages": 100}])
    assert r["total_messages"] == 150
    assert r["non_empty"] == 2
    assert not r["clean"]
