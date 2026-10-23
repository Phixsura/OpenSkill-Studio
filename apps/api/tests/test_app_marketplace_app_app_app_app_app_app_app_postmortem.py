from app.services.app_marketplace_app_app_app_app_app_app_app_postmortem import build_postmortem

def test_postmortem():
    r = build_postmortem(
        title="Database Outage", severity="sev1", duration_min=95,
        impact="All API requests failed for 95 minutes",
        root_cause="Disk space exhaustion on primary DB",
        timeline=[
            {"time": "10:00", "action": "Alerts fired", "by": "PagerDuty"},
            {"time": "10:15", "action": "Identified disk full", "by": "alice"},
            {"time": "11:35", "action": "Resolved", "by": "bob"},
        ],
        action_items=[
            {"task": "Add disk monitoring", "owner": "alice", "priority": "high", "due": "2026-11-01"},
            {"task": "Enable auto-expand", "owner": "bob", "priority": "medium"},
        ],
        authors=["alice", "bob"])
    assert r["mttr_display"] == "1h 35m"
    assert r["total_actions"] == 2
    assert r["high_priority_actions"] == 1
    assert len(r["timeline"]) == 3
