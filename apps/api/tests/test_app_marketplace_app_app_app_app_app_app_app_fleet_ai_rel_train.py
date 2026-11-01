from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_rel_train import fleet_ai_release_train
def test_rt():
    r = fleet_ai_release_train([{"active": True, "services": 50, "releases_24h": 10, "on_time_pct": 95}])
    assert r["services"] == 50
    assert r["punctual"]
