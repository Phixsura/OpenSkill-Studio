from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sqs import fleet_sqs_status
def test_sqs():
    r = fleet_sqs_status([{"messages_visible": 100, "messages_in_flight": 50, "dlq_messages": 5}])
    assert r["dlq_messages"] == 5
    assert not r["clean"]
