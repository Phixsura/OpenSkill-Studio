from app.services.app_marketplace_app_app_app_app_app_app_app_rollout_track import RolloutTracker

def test_advance():
    rt = RolloutTracker()
    rt.start("v2.0", target_pct=100, step_pct=25)
    rt.advance("v2.0")
    rt.advance("v2.0")
    s = rt.status("v2.0")
    assert s["current_pct"] == 50
    assert s["status"] == "in_progress"
    rt.advance("v2.0")
    rt.advance("v2.0")
    s2 = rt.status("v2.0")
    assert s2["status"] == "completed"

def test_rollback():
    rt = RolloutTracker()
    rt.start("v3.0")
    rt.advance("v3.0")
    rt.rollback("v3.0")
    s = rt.status("v3.0")
    assert s["status"] == "rolled_back"
    assert s["current_pct"] == 0
