from app.services.app_marketplace_app_app_app_app_app_app_app_runbook_lib import (
    add_runbook, search_runbooks, use_runbook, runbook_stats, clear_runbooks,
)

def test_search():
    clear_runbooks()
    add_runbook("db-failover", "Database Failover", "infrastructure", ["Check primary", "Promote replica"], ["database"])
    add_runbook("deploy-rollback", "Deployment Rollback", "deployment", ["Identify version", "Rollback"], ["deploy"])
    r = search_runbooks("database")
    assert len(r) == 1
    assert r[0]["slug"] == "db-failover"
    clear_runbooks()

def test_use():
    clear_runbooks()
    add_runbook("test", "Test Runbook", "ops", ["Step 1"])
    use_runbook("test")
    use_runbook("test")
    s = runbook_stats()
    assert s["most_used"] == "Test Runbook"
    clear_runbooks()
