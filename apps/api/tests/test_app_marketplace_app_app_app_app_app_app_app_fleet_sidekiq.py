from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sidekiq import fleet_sidekiq_status
def test_sk():
    r = fleet_sidekiq_status([{"busy": 5, "enqueued": 100, "dead": 3}])
    assert r["enqueued"] == 100
    assert not r["healthy"]
