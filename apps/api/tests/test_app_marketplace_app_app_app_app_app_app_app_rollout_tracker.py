from app.services.app_marketplace_app_app_app_app_app_app_app_rollout_tracker import (
    create_rollout, advance_rollout, pause_rollout, rollout_summary,
)

def test_rollout():
    r = create_rollout("d1", steps=[10, 50, 100])
    a1 = advance_rollout(r)
    assert a1["current_pct"] == 10
    advance_rollout(r)
    assert r["current_pct"] == 50
    advance_rollout(r)
    assert r["status"] == "complete"

def test_pause():
    r = create_rollout("d2")
    advance_rollout(r)
    pause_rollout(r)
    a = advance_rollout(r)
    assert not a["advanced"]

def test_summary():
    rollouts = [create_rollout("a"), create_rollout("b")]
    rollouts[0]["status"] = "complete"
    s = rollout_summary(rollouts)
    assert s["complete"] == 1
    assert s["in_progress"] == 1
