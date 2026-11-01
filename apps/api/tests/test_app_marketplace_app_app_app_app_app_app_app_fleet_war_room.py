from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_war_room import fleet_war_room
def test_war():
    r = fleet_war_room([{"status": "active", "duration_min": 30}, {"status": "resolved", "duration_min": 60}])
    assert r["active"] == 1
    assert not r["calm"]
