from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_tutorial import fleet_ai_tutorial
def test_tut():
    r = fleet_ai_tutorial([{"active": True, "tutorials": 200, "completions_24h": 10000, "rating": 4.7}])
    assert r["tutorials"] == 200
    assert r["popular"]
