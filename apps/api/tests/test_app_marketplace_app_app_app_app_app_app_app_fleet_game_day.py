from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_game_day import fleet_game_day
def test_gd():
    r = fleet_game_day([{"outcome": "passed", "learnings": 2}, {"outcome": "failed", "learnings": 5}])
    assert r["passed"] == 1
    assert r["learnings"] == 7
    assert not r["resilient"]
