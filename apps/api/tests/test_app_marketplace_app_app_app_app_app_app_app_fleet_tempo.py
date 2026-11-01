from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tempo import fleet_tempo_status
def test_tempo():
    r = fleet_tempo_status([{"healthy": True, "traces_per_sec": 5000, "retention_days": 14}])
    assert r["traces_per_sec"] == 5000
    assert r["min_retention_days"] == 14
    assert r["all_healthy"]
