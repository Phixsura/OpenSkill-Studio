from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_complexity import fleet_cognitive_complexity
def test_complexity():
    r = fleet_cognitive_complexity([{"complexity": 10}, {"complexity": 25}, {"complexity": 5}])
    assert r["avg_complexity"] == 13.3
    assert r["high_complexity"] == 1
    assert r["maintainable"]
