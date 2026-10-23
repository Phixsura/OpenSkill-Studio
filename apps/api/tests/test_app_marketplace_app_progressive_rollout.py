from app.services.app_marketplace_app_progressive_rollout import create_rollout, should_promote, advance_rollout

def test_create():
    r = create_rollout(app_id="a1", version_id="v1")
    assert len(r["stages"]) == 4
    assert r["current_stage"] == 0

def test_promote_ok():
    r = should_promote(current_metrics={"error_rate": 0.5, "p99_ms": 200},
                        thresholds={"max_error_rate": 1, "max_p99_ms": 500})
    assert r["promote"]

def test_promote_fail():
    r = should_promote(current_metrics={"error_rate": 5, "p99_ms": 200},
                        thresholds={"max_error_rate": 1, "max_p99_ms": 500})
    assert not r["promote"]

def test_advance():
    rollout = create_rollout(app_id="a1", version_id="v1")
    r = advance_rollout(rollout=rollout)
    assert r["current_stage"] == 1
    assert r["current_pct"] == 25

def test_complete():
    rollout = {"stages": [{"pct": 100}], "current_stage": 0, "status": "active"}
    r = advance_rollout(rollout=rollout)
    assert r["status"] == "completed"
