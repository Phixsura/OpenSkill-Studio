from app.services.app_marketplace_app_app_app_app_app_app_app_postmortem import create_postmortem, postmortem_stats

def test_create():
    r = create_postmortem("INC-1", "Database Outage", "critical",
        [{"time": "10:00", "event": "Alert fired"}],
        "Connection pool exhaustion",
        [{"task": "Add connection limits", "done": True},
         {"task": "Add alerting", "done": False}])
    assert r["action_count"] == 2
    assert r["completed_actions"] == 1
    assert r["progress_pct"] == 50

def test_stats():
    pms = [
        create_postmortem("a", "X", "critical", [], "cause", [{"done": True}]),
        create_postmortem("b", "Y", "major", [], "cause", [{"done": False}, {"done": False}]),
    ]
    s = postmortem_stats(pms)
    assert s["total"] == 2
    assert s["action_completion_pct"] == 33
