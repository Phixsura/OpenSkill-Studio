from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_prog_del import fleet_progressive_delivery
def test_prog():
    r = fleet_progressive_delivery([{"phase": "progressing"}, {"phase": "completed"}, {"phase": "paused"}])
    assert r["in_progress"] == 1
    assert r["completed"] == 1
    assert r["paused"] == 1
