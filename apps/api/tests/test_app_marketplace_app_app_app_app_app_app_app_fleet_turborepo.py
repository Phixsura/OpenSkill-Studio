from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_turborepo import fleet_turborepo_status
def test_turbo():
    r = fleet_turborepo_status([{"cache_status": "HIT", "time_saved_sec": 30}] * 8 + [{"cache_status": "MISS"}] * 2)
    assert r["hit_rate"] == 80.0
    assert r["time_saved_sec"] == 240
