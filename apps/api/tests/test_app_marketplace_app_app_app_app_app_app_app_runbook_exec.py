from app.services.app_marketplace_app_app_app_app_app_app_app_runbook_exec import create_runbook, execute_step, runbook_status

def test_execute():
    rb = create_runbook("Deploy", [
        {"title": "Backup DB", "type": "automated"},
        {"title": "Run Migrations", "type": "automated"},
        {"title": "Verify", "type": "manual"},
    ])
    assert rb["total_steps"] == 3
    r = execute_step(rb, 0)
    assert r["executed"]
    assert r["progress_pct"] == 33
    execute_step(rb, 1)
    execute_step(rb, 2)
    s = runbook_status(rb)
    assert s["status"] == "complete"
    assert s["failed"] == 0
