from app.services.app_marketplace_app_app_app_app_app_app_app_retention_policy import RetentionPolicyManager

def test_retention():
    mgr = RetentionPolicyManager()
    mgr.add_policy(resource="logs", retention_days=90, action="delete")
    mgr.add_policy(resource="analytics", retention_days=365, action="archive", archive_before=True)
    records = [
        {"resource": "logs", "id": "l1", "age_days": 30},
        {"resource": "logs", "id": "l2", "age_days": 120},  # violation
        {"resource": "analytics", "id": "a1", "age_days": 400},  # violation
    ]
    r = mgr.check_compliance(records)
    assert r["compliant"] == 1
    assert r["violation_count"] == 2
    assert not r["all_compliant"]
    assert r["violations"][0]["overdue_days"] == 30
    s = mgr.summary()
    assert s["total_policies"] == 2
