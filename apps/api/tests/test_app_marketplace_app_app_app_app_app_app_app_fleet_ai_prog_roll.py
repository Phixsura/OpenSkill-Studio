from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_prog_roll import fleet_ai_progressive_rollout
def test_pr():
    r = fleet_ai_progressive_rollout([{"active": True, "pct": 50, "stages_done": 3, "total_stages": 5}])
    assert r["current_pct"] == 50.0
    assert r["progressing"]
