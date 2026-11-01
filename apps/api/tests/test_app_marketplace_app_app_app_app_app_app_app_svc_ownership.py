from app.services.app_marketplace_app_app_app_app_app_app_app_svc_ownership import assign_ownership, ownership_matrix

def test_ownership():
    r = assign_ownership([
        {"name": "api", "team": "platform"},
        {"name": "web", "team": "frontend"},
        {"name": "orphan"},
    ])
    assert r["teams"] == ["frontend", "platform"]
    assert r["unowned_count"] == 1
    assert not r["all_owned"]

def test_matrix():
    r = ownership_matrix([
        {"name": "api", "team": "platform", "oncall": "alice", "runbook": True, "docs": True},
        {"name": "db", "team": "data", "oncall": "", "runbook": False, "docs": False},
    ])
    assert r["complete"] == 1
    assert r["completeness_pct"] == 50
