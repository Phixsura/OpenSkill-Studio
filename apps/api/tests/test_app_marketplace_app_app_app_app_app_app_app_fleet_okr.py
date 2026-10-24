from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_okr import fleet_okr_tracker
def test_okr():
    r = fleet_okr_tracker([{"progress_pct": 90}, {"progress_pct": 50}, {"progress_pct": 10}])
    assert r["on_track"] == 1
    assert r["at_risk"] == 1
    assert r["behind"] == 1
    assert r["avg_progress"] == 50.0
